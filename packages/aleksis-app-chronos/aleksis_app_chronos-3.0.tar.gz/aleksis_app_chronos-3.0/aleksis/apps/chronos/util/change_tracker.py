from typing import Any, Optional, Type

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Model
from django.db.models.signals import m2m_changed, post_save, pre_delete
from django.dispatch import Signal, receiver

from celery import shared_task
from reversion.models import Revision


def _get_substitution_models():
    from aleksis.apps.chronos.models import (
        Event,
        ExtraLesson,
        LessonSubstitution,
        SupervisionSubstitution,
    )

    return [LessonSubstitution, Event, ExtraLesson, SupervisionSubstitution]


class TimetableChange:
    """A change to timetable models."""

    def __init__(
        self,
        instance: Model,
        changed_fields: Optional[dict[str, Any]] = None,
        created: bool = False,
        deleted: bool = False,
    ):
        self.instance = instance
        self.changed_fields = changed_fields or {}
        self.created = created
        self.deleted = deleted


class TimetableDataChangeTracker:
    """Helper class for tracking changes in timetable models by using signals."""

    @classmethod
    def get_models(cls) -> list[Type[Model]]:
        """Return all models that should be tracked."""
        from aleksis.apps.chronos.models import (
            Event,
            ExtraLesson,
            LessonSubstitution,
            SupervisionSubstitution,
        )

        return [LessonSubstitution, Event, ExtraLesson, SupervisionSubstitution]

    def __init__(self):
        self.changes = {}
        self.m2m_fields = {}

        if transaction.get_autocommit():
            raise RuntimeError("Cannot use change tracker outside of transaction")

        for model in self.get_models():
            post_save.connect(self._handle_save, sender=model, weak=False)
            pre_delete.connect(self._handle_delete, sender=model, weak=False)

            # Register signals for all relevant m2m fields
            m2m_fields = {
                getattr(model, f.name).through: f
                for f in model._meta.get_fields()
                if f.many_to_many
            }
            self.m2m_fields.update(m2m_fields)
            for through_model, field in m2m_fields.items():
                m2m_changed.connect(self._handle_m2m_changed, sender=through_model, weak=False)

        transaction.on_commit(self.close)

    def get_instance_key(self, instance: Model) -> str:
        """Get unique string key for an instance."""
        return f"{instance._meta.model_name}_{instance.id}"

    def _add_change(self, change: TimetableChange):
        """Add a change to the list of changes and update, if necessary."""
        key = self.get_instance_key(change.instance)
        if key not in self.changes or change.deleted or change.created:
            self.changes[key] = change
        else:
            self.changes[key].changed_fields.update(change.changed_fields)

    def _handle_save(self, sender: Type[Model], instance: Model, created: bool, **kwargs):
        """Handle the save signal."""
        change = TimetableChange(instance, created=created)
        if not created:
            change.changed_fields = instance.tracker.changed()
        self._add_change(change)

    def _handle_delete(self, sender: Type[Model], instance: Model, **kwargs):
        """Handle the delete signal."""
        change = TimetableChange(instance, deleted=True)
        self._add_change(change)

    def _handle_m2m_changed(
        self,
        sender: Type[Model],
        instance: Model,
        action: str,
        model: Type[Model],
        pk_set: set,
        **kwargs,
    ):
        """Handle the m2m_changed signal."""
        if action in ["pre_add", "pre_remove", "pre_clear"]:
            field_name = self.m2m_fields[sender].name
            current_value = list(getattr(instance, field_name).all())
            if self.get_instance_key(instance) in self.changes:
                change = self.changes[self.get_instance_key(instance)]
                if field_name in change.changed_fields:
                    current_value = None

            if current_value is not None:
                change = TimetableChange(instance, changed_fields={field_name: current_value})
                self._add_change(change)

    def close(self):
        """Disconnect signals and send change signal."""
        for model in self.get_models():
            post_save.disconnect(self._handle_save, sender=model)
            pre_delete.disconnect(self._handle_delete, sender=model)

        for through_model, field in self.m2m_fields.items():
            m2m_changed.disconnect(self._handle_m2m_changed, sender=through_model)

        timetable_data_changed.send(sender=self, changes=self.changes)


chronos_revision_created = Signal()
substitutions_changed = Signal()
timetable_data_changed = Signal()


@shared_task
def handle_new_revision(revision_pk: int):
    """Handle a new revision in background using Celery."""
    revision = Revision.objects.get(pk=revision_pk)
    if revision.version_set.filter(content_type__app_label="chronos").exists():
        chronos_revision_created.send(sender=revision)


@receiver(chronos_revision_created)
def handle_substitution_change(sender: Revision, **kwargs):
    """Handle the change of a substitution-like object."""
    # Filter versions by substitution-like models
    content_types = ContentType.objects.get_for_models(*_get_substitution_models()).values()
    versions = sender.version_set.filter(content_type__in=content_types)
    if versions:
        substitutions_changed.send(sender=sender, versions=versions)

from typing import Union

from ..extensions import UnknownType
from ..models.canvas_initialize_webhook import CanvasInitializeWebhook
from ..models.canvas_interaction_webhook import CanvasInteractionWebhook
from ..models.lifecycle_activate_webhook import LifecycleActivateWebhook
from ..models.lifecycle_deactivate_webhook import LifecycleDeactivateWebhook

WebhookMessage = Union[
    CanvasInteractionWebhook,
    CanvasInitializeWebhook,
    LifecycleActivateWebhook,
    LifecycleDeactivateWebhook,
    UnknownType,
]

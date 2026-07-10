import 'package:flutter/material.dart';

/// In-app notification service.
///
/// Phase 1 strategy: foreground-resume polling only.
/// Push notifications (FCM/APNs) require a backend delivery mechanism —
/// TODO(OQ-01): implement once backend push endpoint is available.
///
/// Responsibilities:
/// - Foreground-resume check for pending variants
/// - Client-side token expiry watch (24h window)
/// - In-app snackbar / banner delivery
class NotificationService {
  NotificationService._();

  static final NotificationService instance = NotificationService._();

  /// Shows an in-app snackbar notification.
  void showSnackbar(
    BuildContext context, {
    required String message,
    Duration duration = const Duration(seconds: 4),
    SnackBarAction? action,
  }) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        duration: duration,
        action: action,
      ),
    );
  }

  /// Shows a persistent banner (must be dismissed).
  void showBanner(
    BuildContext context, {
    required String message,
    required List<Widget> actions,
  }) {
    ScaffoldMessenger.of(context).showMaterialBanner(
      MaterialBanner(
        content: Text(message),
        actions: actions,
      ),
    );
  }

  // ── TODO: Push notification stub ─────────────────────────────────────────
  //
  // Push delivery requires:
  // 1. A backend endpoint to register FCM/APNs device tokens.
  // 2. Firebase Messaging dependency (firebase_messaging).
  // 3. Platform-level permission request (iOS).
  //
  // When implemented:
  // - Register device token on login via POST /api/push/register (TODO endpoint)
  // - Handle onMessage (foreground) via FirebaseMessaging.onMessage.listen(...)
  // - Handle onBackgroundMessage (background) via top-level handler
  // - Deep-link targets per NotificationMatrix (Phase 9 of plan)
  //
  // Frequency cap: max 1 expiry warning per variant per session.
  // Quiet hours: respect device DND settings via platform channel.
}

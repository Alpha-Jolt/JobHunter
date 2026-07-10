import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Mixin that sets FLAG_SECURE on Android (prevents screenshots and
/// appearance in the recents screen) when the widget is visible.
///
/// On iOS, Flutter renders into a UIView — full FLAG_SECURE equivalent
/// is not universally enforceable. Setting `isOpaque: true` on the route
/// (done in GoRouter) prevents content leakage on app background; this
/// mixin focuses on Android.
///
/// Usage: add `with _SecureScreenMixin` to a [State] class.
mixin SecureScreenMixin<T extends StatefulWidget> on State<T> {
  static const _channel = MethodChannel('jobhunter/secure_screen');

  @override
  void initState() {
    super.initState();
    _setSecure(true);
  }

  @override
  void dispose() {
    _setSecure(false);
    super.dispose();
  }

  Future<void> _setSecure(bool secure) async {
    try {
      await _channel.invokeMethod<void>('setSecure', {'secure': secure});
    } on MissingPluginException {
      // Platform channel not yet implemented — best-effort, not a hard failure.
      // iOS does not support FLAG_SECURE natively.
    } catch (_) {
      // Silently ignore — security hardening is best-effort on unsupported platforms.
    }
  }
}

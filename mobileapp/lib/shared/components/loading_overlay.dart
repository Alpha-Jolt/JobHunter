import 'package:flutter/material.dart';
import '../../core/theme/app_spacing.dart';
import 'app_button.dart';

/// Full-screen blocking overlay shown during network-mandatory operations
/// (variant generation, approval, application send).
/// Cannot be dismissed by the user — action must complete or fail.
class LoadingOverlay extends StatelessWidget {
  const LoadingOverlay({
    required this.message,
    super.key,
  });

  final String message;

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.black.withValues(alpha: 0.5),
      child: Center(
        child: Card(
          margin: const EdgeInsets.all(AppSpacing.xl3),
          child: Padding(
            padding: const EdgeInsets.all(AppSpacing.xl3),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const CircularProgressIndicator(),
                const SizedBox(height: AppSpacing.xl2),
                Text(
                  message,
                  style: Theme.of(context).textTheme.bodyLarge,
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  /// Wraps [child] with this overlay when [isVisible] is true.
  static Widget wrap({
    required Widget child,
    required bool isVisible,
    String message = 'Please wait…',
  }) {
    return Stack(
      children: [
        child,
        if (isVisible)
          LoadingOverlay(message: message),
      ],
    );
  }
}

import 'package:flutter/material.dart';
import '../../core/theme/app_spacing.dart';

/// Full-screen blocking overlay shown during network-mandatory operations
/// (variant generation, approval, application send).
///
/// Usage 1 — wrapping widget (most common):
///   LoadingOverlay(isLoading: _isLoading, child: Scaffold(...))
///
/// Usage 2 — overlay widget only (placed in a Stack):
///   if (isLoading) LoadingOverlay.standalone(message: 'Please wait…')
class LoadingOverlay extends StatelessWidget {
  const LoadingOverlay({
    required this.child,
    this.isLoading = false,
    this.message = 'Please wait…',
    super.key,
  });

  final Widget child;
  final bool isLoading;
  final String message;

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        child,
        if (isLoading)
          Positioned.fill(
            child: Container(
              color: Colors.black.withValues(alpha: 0.45),
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
            ),
          ),
      ],
    );
  }

  /// Convenience static method for backward compat.
  static Widget wrap({
    required Widget child,
    required bool isVisible,
    String message = 'Please wait…',
  }) =>
      LoadingOverlay(
        isLoading: isVisible,
        message: message,
        child: child,
      );
}

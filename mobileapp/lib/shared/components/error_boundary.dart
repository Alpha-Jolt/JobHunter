import 'package:flutter/material.dart';
import '../../core/theme/app_spacing.dart';
import 'app_button.dart';

/// Per-tab error boundary widget.
///
/// Catches unhandled exceptions from a single feature tab and renders
/// a recovery UI without crashing the entire app — mirroring the
/// backend's module-isolation principle.
///
/// Usage: wrap each tab's root widget in [ErrorBoundaryWidget].
class ErrorBoundaryWidget extends StatefulWidget {
  const ErrorBoundaryWidget({
    required this.child,
    required this.tabLabel,
    super.key,
  });

  final Widget child;
  final String tabLabel;

  @override
  State<ErrorBoundaryWidget> createState() => _ErrorBoundaryWidgetState();
}

class _ErrorBoundaryWidgetState extends State<ErrorBoundaryWidget> {
  Object? _error;

  void _reset() => setState(() => _error = null);

  @override
  Widget build(BuildContext context) {
    if (_error != null) {
      return _ErrorBoundaryFallback(
        tabLabel: widget.tabLabel,
        onRetry: _reset,
      );
    }
    return widget.child;
  }

  // Called by the global FlutterError handler to inject errors
  // into the boundary for a specific tab.
  void handleError(Object error) {
    if (mounted) setState(() => _error = error);
  }
}

/// Fallback UI shown inside a single tab when it catches an unhandled error.
/// Distinct from [ErrorBanner] — this is a full-screen boundary fallback,
/// not an inline data-load error.
class _ErrorBoundaryFallback extends StatelessWidget {
  const _ErrorBoundaryFallback({
    required this.tabLabel,
    required this.onRetry,
  });

  final String tabLabel;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.xl3),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.warning_amber_outlined,
                size: 56,
                color: theme.colorScheme.error,
              ),
              const SizedBox(height: AppSpacing.xl2),
              Text(
                'Something went wrong',
                style: theme.textTheme.titleLarge,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: AppSpacing.sm),
              Text(
                'The $tabLabel section encountered an unexpected error.',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: AppSpacing.xl3),
              AppButton(
                label: 'Try Again',
                onPressed: onRetry,
                icon: Icons.refresh_outlined,
                fullWidth: false,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

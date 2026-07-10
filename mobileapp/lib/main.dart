import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/network/dio_client.dart';
import 'core/router/app_router.dart';
import 'core/theme/app_theme.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // ── Global exception boundary ───────────────────────────────────────────
  // Catches unhandled Flutter framework errors (widget build errors, etc.)
  // Logs in debug; silenced in production — never exposes stack traces to users.
  FlutterError.onError = (FlutterErrorDetails details) {
    if (kDebugMode) {
      FlutterError.dumpErrorToConsole(details);
    }
    // In production, forward to crash reporting service when available.
    // PII redaction rule: never log resume content or tokens.
  };

  // Catches unhandled async errors outside the Flutter widget layer
  // (e.g., isolate errors, platform channel errors).
  PlatformDispatcher.instance.onError = (error, stack) {
    if (kDebugMode) {
      debugPrint('[PlatformDispatcher] Unhandled: $error');
    }
    // Fail-closed: no approval-gated or send action should silently
    // complete after an unhandled exception — they all require explicit
    // user confirmation which cannot proceed past an exception.
    return true; // handled
  };

  // Initialise the singleton Dio client (creates cookie jar, sets base URL)
  await DioClient.init();

  runApp(
    const ProviderScope(
      child: JobHunterApp(),
    ),
  );
}

class JobHunterApp extends ConsumerWidget {
  const JobHunterApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);

    return MaterialApp.router(
      title: 'JobHunter',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      themeMode: ThemeMode.system,
      routerConfig: router,
      // Widget-level exception UI — shown for errors that escape all boundaries.
      builder: (context, child) => _GlobalErrorWidget(child: child),
    );
  }
}

/// Last-resort widget boundary wrapping the entire app router output.
/// Only fires if a tab-level [ErrorBoundaryWidget] did not catch the error.
class _GlobalErrorWidget extends StatelessWidget {
  const _GlobalErrorWidget({required this.child});
  final Widget? child;

  @override
  Widget build(BuildContext context) {
    ErrorWidget.builder = (FlutterErrorDetails details) {
      if (kDebugMode) return ErrorWidget(details.exception);
      // Production: calm fallback — no stack trace shown.
      return Scaffold(
        body: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error_outline, size: 48),
              const SizedBox(height: 16),
              Text(
                'Something went wrong. Please restart the app.',
                style: Theme.of(context).textTheme.bodyMedium,
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      );
    };
    return child ?? const SizedBox.shrink();
  }
}

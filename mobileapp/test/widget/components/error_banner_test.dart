import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:jobhunter/core/network/app_error.dart';
import 'package:jobhunter/shared/components/error_banner.dart';

void main() {
  Widget _wrap(Widget child) => MaterialApp(home: Scaffold(body: child));

  group('ErrorBanner — standard error', () {
    testWidgets('shows message text', (tester) async {
      // Arrange + Act
      await tester.pumpWidget(
        _wrap(const ErrorBanner(message: 'Something went wrong.')),
      );

      // Assert
      expect(find.text('Something went wrong.'), findsOneWidget);
    });

    testWidgets('shows Retry button when isRetryable and onRetry provided',
        (tester) async {
      // Arrange
      var retried = false;

      // Act
      await tester.pumpWidget(
        _wrap(ErrorBanner(
          message: 'Error',
          isRetryable: true,
          onRetry: () => retried = true,
        )),
      );
      await tester.tap(find.text('Retry'));
      await tester.pump();

      // Assert
      expect(retried, isTrue);
    });

    testWidgets('hides Retry button when isRetryable is false', (tester) async {
      // Arrange + Act
      await tester.pumpWidget(
        _wrap(const ErrorBanner(message: 'Error', isRetryable: false)),
      );

      // Assert
      expect(find.text('Retry'), findsNothing);
    });
  });

  group('ErrorBanner — schemaMismatch tier', () {
    testWidgets('shows update icon and no Retry button', (tester) async {
      // Arrange
      final error = AppError.schemaMismatch('field missing');

      // Act
      await tester.pumpWidget(
        _wrap(ErrorBanner.fromError(error)),
      );

      // Assert
      expect(find.byIcon(Icons.system_update_outlined), findsOneWidget);
      expect(find.text('Retry'), findsNothing);
    });
  });

  group('ErrorBanner — conflict tier', () {
    testWidgets('shows info icon for conflict errors', (tester) async {
      // Arrange
      final error = AppError.fromStatusCode(409, body: 'Already applied');

      // Act
      await tester.pumpWidget(
        _wrap(ErrorBanner.fromError(error)),
      );

      // Assert
      expect(find.byIcon(Icons.info_outline), findsOneWidget);
    });
  });
}

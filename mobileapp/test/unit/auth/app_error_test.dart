import 'package:flutter_test/flutter_test.dart';
import 'package:jobhunter/core/network/app_error.dart';

void main() {
  group('AppError.fromStatusCode — conflict sub-types', () {
    test('duplicate application message', () {
      final error = AppError.fromStatusCode(
        409,
        body: 'Already applied to this job',
      );
      expect(error.type, AppErrorType.conflict);
      expect(error.userMessage, contains("already applied"));
    });

    test('daily limit message contains limit number', () {
      final error = AppError.fromStatusCode(
        409,
        body: 'Daily limit exceeded',
      );
      expect(error.type, AppErrorType.conflict);
      expect(error.userMessage, contains('10'));
    });

    test('duplicate variant message', () {
      final error = AppError.fromStatusCode(
        409,
        body: 'Duplicate variant already exists',
      );
      expect(error.type, AppErrorType.conflict);
      expect(error.userMessage, contains('variant'));
    });

    test('token already used message', () {
      final error = AppError.fromStatusCode(
        409,
        body: 'Token already used',
      );
      expect(error.type, AppErrorType.conflict);
      expect(error.userMessage, contains('processed'));
    });
  });

  group('AppError.fromStatusCode — other status codes', () {
    test('401 maps to invalidCredentials', () {
      final error = AppError.fromStatusCode(401);
      expect(error.type, AppErrorType.invalidCredentials);
      expect(error.isRetryable, isFalse);
    });

    test('429 maps to rateLimited and is retryable', () {
      final error = AppError.fromStatusCode(429);
      expect(error.type, AppErrorType.rateLimited);
      expect(error.isRetryable, isTrue);
    });

    test('500 maps to serverError and is retryable', () {
      final error = AppError.fromStatusCode(500);
      expect(error.type, AppErrorType.serverError);
      expect(error.isRetryable, isTrue);
    });

    test('404 maps to notFound and is not retryable', () {
      final error = AppError.fromStatusCode(404);
      expect(error.type, AppErrorType.notFound);
      expect(error.isRetryable, isFalse);
    });
  });

  group('AppError.networkUnavailable', () {
    test('is retryable with networkUnavailable type', () {
      final error = AppError.networkUnavailable();
      expect(error.type, AppErrorType.networkUnavailable);
      expect(error.isRetryable, isTrue);
    });
  });

  group('AppError.schemaMismatch', () {
    test('has schemaMismatch type and is not retryable', () {
      final error = AppError.schemaMismatch('field x missing');
      expect(error.type, AppErrorType.schemaMismatch);
      expect(error.isRetryable, isFalse);
    });
  });
}

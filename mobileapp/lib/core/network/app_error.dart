/// Typed application error model.
///
/// All API call failures are converted into [AppError] at the repository layer.
/// Business-rule errors (approval gates, rate limits) use distinct [AppErrorType]
/// values so the UI can render them calmly rather than as unexpected failures.
enum AppErrorType {
  validation,         // 400
  invalidCredentials, // 401 wrong password
  sessionExpired,     // 401 token expired — handled silently by interceptor
  forbidden,          // 403
  notFound,           // 404
  conflict,           // 409 — business rule: duplicate, limit, already processed
  rateLimited,        // 429
  serverError,        // 5xx
  networkUnavailable, // no connectivity
  schemaMismatch,     // deserialization failure — contract drift
  unknown,
}

class AppError implements Exception {
  const AppError({
    required this.type,
    required this.userMessage,
    this.statusCode,
    this.technicalDetail,
    this.isRetryable = false,
  });

  final AppErrorType type;
  final String userMessage;
  final int? statusCode;

  /// Never shown to users. For logging/debugging only.
  final String? technicalDetail;
  final bool isRetryable;

  /// Parse a Dio response error into a typed [AppError].
  factory AppError.fromStatusCode(int statusCode, {String? body}) {
    switch (statusCode) {
      case 400:
        return AppError(
          type: AppErrorType.validation,
          statusCode: statusCode,
          userMessage: 'Please check your input and try again.',
          technicalDetail: body,
        );
      case 401:
        return AppError(
          type: AppErrorType.invalidCredentials,
          statusCode: statusCode,
          userMessage: 'Incorrect email or password.',
          technicalDetail: body,
        );
      case 403:
        return AppError(
          type: AppErrorType.forbidden,
          statusCode: statusCode,
          userMessage: "You don't have permission for this action.",
          technicalDetail: body,
        );
      case 404:
        return AppError(
          type: AppErrorType.notFound,
          statusCode: statusCode,
          userMessage: 'The requested resource was not found.',
          technicalDetail: body,
        );
      case 409:
        // Business-rule conflicts — calm, expected-state treatment.
        // The backend body distinguishes sub-types; map them explicitly.
        final conflictMessage = _mapConflictBody(body);
        return AppError(
          type: AppErrorType.conflict,
          statusCode: statusCode,
          userMessage: conflictMessage,
          technicalDetail: body,
        );
      case 429:
        return AppError(
          type: AppErrorType.rateLimited,
          statusCode: statusCode,
          userMessage:
              'Please wait a moment before trying again.',
          isRetryable: true,
          technicalDetail: body,
        );
      default:
        return AppError(
          type: AppErrorType.serverError,
          statusCode: statusCode,
          userMessage: 'Something went wrong on our end. Please try again.',
          isRetryable: true,
          technicalDetail: body,
        );
    }
  }

  static AppError networkUnavailable() => const AppError(
        type: AppErrorType.networkUnavailable,
        userMessage: 'No internet connection.',
        isRetryable: true,
      );

  static AppError schemaMismatch(String detail) => AppError(
        type: AppErrorType.schemaMismatch,
        userMessage:
            'Unexpected response from server. The app may need an update.',
        technicalDetail: detail,
      );

  static AppError unknown(String? detail) => AppError(
        type: AppErrorType.unknown,
        userMessage: 'An unexpected error occurred. Please try again.',
        isRetryable: true,
        technicalDetail: detail,
      );

  @override
  String toString() => 'AppError(type: $type, status: $statusCode, '
      'message: $userMessage)';
}

/// Maps a 409 conflict response body to a specific, calm user-facing message.
/// Business-rule conflicts are expected states — never shown as failures.
String _mapConflictBody(String? body) {
  if (body == null) return 'This action conflicts with the current state.';
  final lower = body.toLowerCase();
  if (lower.contains('already applied') || lower.contains('duplicate application')) {
    return "You've already applied to this job.";
  }
  if (lower.contains('daily limit') || lower.contains('limit exceeded')) {
    return "You've reached today's application limit (10). Come back tomorrow.";
  }
  if (lower.contains('already approved') || lower.contains('token') && lower.contains('used')) {
    return 'This variant has already been processed.';
  }
  if (lower.contains('duplicate variant') || lower.contains('already exists')) {
    return 'You already have a variant for this job.';
  }
  return body;
}

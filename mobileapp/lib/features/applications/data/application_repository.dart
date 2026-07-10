import 'package:dio/dio.dart';
import '../../../core/network/api_endpoints.dart';
import '../../../core/network/app_error.dart';
import '../../../core/network/dio_client.dart';
import 'application_models.dart';

/// Repository for mail/application operations.
/// POST /api/mail/send is network-mandatory — no offline fallback.
class ApplicationRepository {
  const ApplicationRepository({required DioClient dioClient})
      : _client = dioClient;

  final DioClient _client;

  /// Send an application email.
  /// Subject to 5-gate validation on the backend:
  /// approved variant, no duplicate, daily limit (10), 30s rate limit, job has email.
  Future<ApplicationRecord> send(SendApplicationRequest request) async {
    try {
      final response = await _client.dio.post(
        ApiEndpoints.mailSend,
        data: request.toJson(),
      );
      return ApplicationRecord.fromJson(
          response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  /// Get status of a single application.
  Future<ApplicationStatus> getStatus(String applicationId) async {
    try {
      final response = await _client.dio.get(
        ApiEndpoints.mailStatus(applicationId),
      );
      return ApplicationStatus.fromJson(
          response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  /// Get applications sent today with the count.
  Future<SentTodayResponse> getSentToday(String userId) async {
    try {
      final response = await _client.dio.get(
        ApiEndpoints.mailSentToday(userId),
      );
      return SentTodayResponse.fromJson(
          response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }
}

import 'package:dio/dio.dart';
import '../../../core/network/api_endpoints.dart';
import '../../../core/network/app_error.dart';
import '../../../core/network/dio_client.dart';
import 'job_models.dart';

/// Repository for job discovery data.
class JobRepository {
  const JobRepository({required DioClient dioClient}) : _client = dioClient;

  final DioClient _client;

  /// Fetch a paginated list of active jobs with optional filters.
  Future<JobListResponse> getLatestJobs({
    int page = 1,
    int pageSize = 20,
    JobFilters filters = JobFilters.empty,
  }) async {
    try {
      final queryParams = {
        'page': page,
        'page_size': pageSize,
        ...filters.toQueryParams(),
      };
      final response = await _client.dio.get(
        ApiEndpoints.latestJobs,
        queryParameters: queryParams,
      );
      return JobListResponse.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  /// Fetch job counts grouped by source, status, and email trust.
  Future<JobCountsResponse> getCounts() async {
    try {
      final response =
          await _client.dio.get(ApiEndpoints.jobCounts);
      return JobCountsResponse.fromJson(
          response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }
}

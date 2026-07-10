import 'package:dio/dio.dart';
import '../../../core/network/api_endpoints.dart';
import '../../../core/network/app_error.dart';
import '../../../core/network/dio_client.dart';
import '../../profile/data/profile_models.dart';

/// Handles resume upload to MinIO via the orchestration API.
class ResumeRepository {
  const ResumeRepository({required DioClient dioClient})
      : _client = dioClient;

  final DioClient _client;

  /// Upload a PDF or DOCX master resume.
  /// Returns [MasterResume] metadata on success.
  Future<MasterResume> upload(String filePath, String fileName) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(filePath, filename: fileName),
      });
      final response = await _client.dio.post(
        ApiEndpoints.resumeUpload,
        data: formData,
        options: Options(
          contentType: 'multipart/form-data',
        ),
      );
      return MasterResume.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }
}

import 'package:dio/dio.dart';
import '../../../core/network/api_endpoints.dart';
import '../../../core/network/app_error.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/storage/secure_storage.dart';
import 'auth_models.dart';

/// Handles all auth API calls.
/// All methods throw [AppError] on failure.
class AuthRepository {
  AuthRepository({
    required DioClient dioClient,
    required SecureStorage secureStorage,
  })  : _dio = dioClient,
        _storage = secureStorage;

  final DioClient _dio;
  final SecureStorage _storage;

  /// Register a new hunter account.
  Future<UserRecord> register(RegisterRequest request) async {
    try {
      final response = await _dio.dio.post(
        ApiEndpoints.register,
        data: request.toJson(),
      );
      return UserRecord.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw extractAppError(e);
    }
  }

  /// Login and set the access token in the Dio client.
  /// The refresh token is set as an httpOnly cookie by the server.
  Future<UserRecord> login(LoginRequest request) async {
    try {
      final response = await _dio.dio.post(
        ApiEndpoints.login,
        data: request.toJson(),
      );
      final loginResponse = LoginResponse.fromJson(
        response.data as Map<String, dynamic>,
      );
      _dio.setAccessToken(loginResponse.accessToken);
      return await getMe();
    } on DioException catch (e) {
      throw extractAppError(e);
    }
  }

  /// Silently refresh the access token using the httpOnly refresh cookie.
  Future<bool> refreshToken() async {
    try {
      final response = await _dio.dio.post(ApiEndpoints.refresh);
      final token = response.data['access_token'] as String?;
      if (token == null) return false;
      _dio.setAccessToken(token);
      return true;
    } on DioException {
      _dio.clearAccessToken();
      return false;
    }
  }

  /// Fetch the current authenticated user record.
  Future<UserRecord> getMe() async {
    try {
      final response = await _dio.dio.get(ApiEndpoints.me);
      return UserRecord.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw extractAppError(e);
    }
  }

  /// Logout — revokes refresh token on server and clears local state.
  Future<void> logout() async {
    try {
      await _dio.dio.post(ApiEndpoints.logout);
    } catch (_) {
      // Best effort — always clear local state regardless
    } finally {
      _dio.clearAccessToken();
      await _storage.clearAll();
    }
  }

  /// Change password for the authenticated user.
  Future<void> changePassword(ChangePasswordRequest request) async {
    try {
      await _dio.dio.patch(
        ApiEndpoints.changePassword,
        data: request.toJson(),
      );
    } on DioException catch (e) {
      throw extractAppError(e);
    }
  }
}

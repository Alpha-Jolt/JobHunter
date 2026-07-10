import 'dart:io';
import 'package:cookie_jar/cookie_jar.dart';
import 'package:dio/dio.dart';
import 'package:dio_cookie_manager/dio_cookie_manager.dart';
import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';
import 'app_error.dart';

/// Base URL is injected at build time via --dart-define=API_BASE_URL=...
/// Default: Android emulator localhost.
const String _kDefaultBaseUrl = 'http://10.0.2.2:8000';

/// Singleton Dio client.
///
/// Responsibilities:
/// - Persisted cookie jar for httpOnly refresh_token cookie
/// - In-memory access token (never written to disk)
/// - Transparent 401 → silent refresh → retry interceptor
/// - All failures converted to typed [AppError]
class DioClient {
  DioClient._();

  static DioClient? _instance;
  static DioClient get instance => _instance!;

  late final Dio _dio;
  late final PersistCookieJar _cookieJar;

  String? _accessToken;

  /// Called by GoRouter redirect on unrecoverable 401.
  void Function()? onSessionExpired;

  static Future<DioClient> init() async {
    if (_instance != null) return _instance!;
    final client = DioClient._();
    await client._setup();
    _instance = client;
    return client;
  }

  Future<void> _setup() async {
    final dir = await getApplicationDocumentsDirectory();
    _cookieJar = PersistCookieJar(
      storage: FileStorage('${dir.path}/.cookies/'),
    );

    final baseUrl = const String.fromEnvironment(
      'API_BASE_URL',
      defaultValue: _kDefaultBaseUrl,
    );

    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 30),
      headers: {'Accept': 'application/json'},
    ));

    _dio.interceptors.addAll([
      CookieManager(_cookieJar),
      _AuthInterceptor(this),
      _ErrorInterceptor(),
    ]);
  }

  Dio get dio => _dio;

  void setAccessToken(String token) {
    _accessToken = token;
    _dio.options.headers['Authorization'] = 'Bearer $token';
  }

  void clearAccessToken() {
    _accessToken = null;
    _dio.options.headers.remove('Authorization');
  }

  bool get hasAccessToken => _accessToken != null;
}

/// Silently refreshes on 401 and retries the original request.
class _AuthInterceptor extends Interceptor {
  _AuthInterceptor(this._client);

  final DioClient _client;
  bool _isRefreshing = false;

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    final statusCode = err.response?.statusCode;
    final path = err.requestOptions.path;

    if (statusCode == 401 && !path.contains('/api/auth/refresh')) {
      if (_isRefreshing) return handler.next(err);
      _isRefreshing = true;
      try {
        final response = await _client.dio.post('/api/auth/refresh');
        final newToken = response.data['access_token'] as String?;
        if (newToken != null) {
          _client.setAccessToken(newToken);
          final opts = err.requestOptions;
          opts.headers['Authorization'] = 'Bearer $newToken';
          final retryResponse = await _client.dio.fetch(opts);
          return handler.resolve(retryResponse);
        }
      } catch (_) {
        _client.clearAccessToken();
        _client.onSessionExpired?.call();
      } finally {
        _isRefreshing = false;
      }
    }
    handler.next(err);
  }
}

/// Converts all Dio failures to typed [AppError].
class _ErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    AppError appError;

    final isConnectionError = err.type == DioExceptionType.connectionError ||
        (err.type == DioExceptionType.unknown && err.error is SocketException);

    if (isConnectionError) {
      appError = AppError.networkUnavailable();
    } else if (err.response != null) {
      final statusCode = err.response!.statusCode ?? 0;
      final body = _extractMessage(err.response!.data);
      appError = AppError.fromStatusCode(statusCode, body: body);
    } else {
      appError = AppError.unknown(err.message);
    }

    if (kDebugMode) {
      debugPrint('[DioClient] ${appError.type}: ${appError.technicalDetail}');
    }

    handler.next(
      DioException(
        requestOptions: err.requestOptions,
        response: err.response,
        type: err.type,
        error: appError,
        message: appError.userMessage,
      ),
    );
  }

  String? _extractMessage(dynamic data) {
    if (data is Map) {
      return (data['detail'] ?? data['message'])?.toString();
    }
    return data?.toString();
  }
}

/// Extracts a typed [AppError] from a caught exception.
AppError extractAppError(Object error) {
  if (error is DioException && error.error is AppError) {
    return error.error as AppError;
  }
  return AppError.unknown(error.toString());
}

import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:dio/dio.dart';

import 'package:jobhunter/core/network/dio_client.dart';
import 'package:jobhunter/core/network/app_error.dart';
import 'package:jobhunter/core/storage/secure_storage.dart';
import 'package:jobhunter/features/auth/data/auth_models.dart';
import 'package:jobhunter/features/auth/data/auth_repository.dart';

import 'auth_repository_test.mocks.dart';

@GenerateMocks([DioClient, SecureStorage, Dio])
void main() {
  late MockDioClient mockDioClient;
  late MockSecureStorage mockSecureStorage;
  late MockDio mockDio;
  late AuthRepository repository;

  setUp(() {
    mockDioClient = MockDioClient();
    mockSecureStorage = MockSecureStorage();
    mockDio = MockDio();
    when(mockDioClient.dio).thenReturn(mockDio);
    repository = AuthRepository(
      dioClient: mockDioClient,
      secureStorage: mockSecureStorage,
    );
  });

  group('AuthRepository.login', () {
    test('sets access token and returns UserRecord on success', () async {
      // Arrange
      when(mockDio.post(any, data: anyNamed('data'))).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: ''),
          statusCode: 200,
          data: {'access_token': 'test_token', 'token_type': 'bearer'},
        ),
      );
      when(mockDio.get(any)).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: ''),
          statusCode: 200,
          data: {
            'user_id': 'u1',
            'email': 'test@example.com',
            'role': 'hunter',
          },
        ),
      );

      // Act
      final result = await repository.login(
        LoginRequest(email: 'test@example.com', password: 'password123'),
      );

      // Assert
      expect(result.userId, 'u1');
      expect(result.email, 'test@example.com');
      verify(mockDioClient.setAccessToken('test_token')).called(1);
    });

    test('throws AppError on 401 invalid credentials', () async {
      // Arrange
      when(mockDio.post(any, data: anyNamed('data'))).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: ''),
          response: Response(
            requestOptions: RequestOptions(path: ''),
            statusCode: 401,
            data: {'detail': 'Invalid credentials'},
          ),
          type: DioExceptionType.badResponse,
          error: AppError.fromStatusCode(401, body: 'Invalid credentials'),
        ),
      );

      // Act + Assert
      expect(
        () => repository.login(
          LoginRequest(email: 'bad@example.com', password: 'wrong'),
        ),
        throwsA(isA<AppError>()),
      );
    });
  });

  group('AuthRepository.refreshToken', () {
    test('sets new access token and returns true on success', () async {
      // Arrange
      when(mockDio.post(any)).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: ''),
          statusCode: 200,
          data: {'access_token': 'new_token'},
        ),
      );

      // Act
      final result = await repository.refreshToken();

      // Assert
      expect(result, isTrue);
      verify(mockDioClient.setAccessToken('new_token')).called(1);
    });

    test('clears token and returns false on DioException', () async {
      // Arrange
      when(mockDio.post(any)).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: ''),
          type: DioExceptionType.connectionError,
        ),
      );

      // Act
      final result = await repository.refreshToken();

      // Assert
      expect(result, isFalse);
      verify(mockDioClient.clearAccessToken()).called(1);
    });
  });

  group('AuthRepository.logout', () {
    test('clears access token and storage regardless of API failure', () async {
      // Arrange — API throws, but logout must still clear local state
      when(mockDio.post(any)).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: ''),
          type: DioExceptionType.connectionError,
        ),
      );
      when(mockSecureStorage.clearAll()).thenAnswer((_) async {});

      // Act
      await repository.logout();

      // Assert — local state cleared even when network fails
      verify(mockDioClient.clearAccessToken()).called(1);
      verify(mockSecureStorage.clearAll()).called(1);
    });
  });

  group('AuthRepository.changePassword', () {
    test('completes without throwing on 200', () async {
      // Arrange
      when(mockDio.patch(any, data: anyNamed('data'))).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: ''),
          statusCode: 200,
          data: {'message': 'ok'},
        ),
      );

      // Act + Assert — no exception thrown
      await expectLater(
        repository.changePassword(
          ChangePasswordRequest(
            currentPassword: 'old',
            newPassword: 'new_secure_pass',
          ),
        ),
        completes,
      );
    });
  });
}

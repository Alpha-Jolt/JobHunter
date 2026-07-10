import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:dio/dio.dart';

import 'package:jobhunter/core/network/dio_client.dart';
import 'package:jobhunter/core/network/app_error.dart';
import 'package:jobhunter/features/applications/data/application_models.dart';
import 'package:jobhunter/features/applications/data/application_repository.dart';

import 'application_repository_test.mocks.dart';

@GenerateMocks([DioClient, Dio])
void main() {
  late MockDioClient mockDioClient;
  late MockDio mockDio;
  late ApplicationRepository repository;

  setUp(() {
    mockDioClient = MockDioClient();
    mockDio = MockDio();
    when(mockDioClient.dio).thenReturn(mockDio);
    repository = ApplicationRepository(dioClient: mockDioClient);
  });

  group('ApplicationRepository.send', () {
    final validRequest = SendApplicationRequest(
      userId: 'u1',
      jobId: 'j1',
      variantId: 'v1',
      userName: 'Test User',
      userEmail: 'test@example.com',
    );

    test('returns ApplicationRecord on success', () async {
      // Arrange
      when(mockDio.post(any, data: anyNamed('data'))).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: ''),
          statusCode: 200,
          data: {
            'application_id': 'a1',
            'user_id': 'u1',
            'job_id': 'j1',
            'resume_variant_id': 'v1',
            'status': 'sent',
          },
        ),
      );

      // Act
      final result = await repository.send(validRequest);

      // Assert
      expect(result.applicationId, 'a1');
      expect(result.status, 'sent');
    });

    test('throws AppError with conflict type on 409 duplicate application', () async {
      // Arrange — already applied to this job
      when(mockDio.post(any, data: anyNamed('data'))).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: ''),
          response: Response(
            requestOptions: RequestOptions(path: ''),
            statusCode: 409,
            data: {'detail': 'Already applied'},
          ),
          type: DioExceptionType.badResponse,
          error: AppError.fromStatusCode(409, body: 'Already applied'),
        ),
      );

      // Act + Assert
      await expectLater(
        () => repository.send(validRequest),
        throwsA(
          isA<AppError>().having((e) => e.type, 'type', AppErrorType.conflict),
        ),
      );
    });

    test('throws AppError with conflict type on 409 daily limit', () async {
      // Arrange
      when(mockDio.post(any, data: anyNamed('data'))).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: ''),
          response: Response(
            requestOptions: RequestOptions(path: ''),
            statusCode: 409,
            data: {'detail': 'Daily limit exceeded'},
          ),
          type: DioExceptionType.badResponse,
          error: AppError.fromStatusCode(409, body: 'Daily limit exceeded'),
        ),
      );

      // Act + Assert
      await expectLater(
        () => repository.send(validRequest),
        throwsA(
          isA<AppError>()
              .having((e) => e.type, 'type', AppErrorType.conflict)
              .having((e) => e.userMessage, 'message', contains('10')),
        ),
      );
    });

    test('throws AppError with rateLimited type on 429', () async {
      // Arrange — 30s rate limit
      when(mockDio.post(any, data: anyNamed('data'))).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: ''),
          response: Response(
            requestOptions: RequestOptions(path: ''),
            statusCode: 429,
            data: {'detail': 'Rate limit'},
          ),
          type: DioExceptionType.badResponse,
          error: AppError.fromStatusCode(429),
        ),
      );

      // Act + Assert
      await expectLater(
        () => repository.send(validRequest),
        throwsA(
          isA<AppError>()
              .having((e) => e.type, 'type', AppErrorType.rateLimited)
              .having((e) => e.isRetryable, 'isRetryable', isTrue),
        ),
      );
    });
  });

  group('ApplicationRepository.getSentToday', () {
    test('returns SentTodayResponse with correct count', () async {
      // Arrange
      when(mockDio.get(any)).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: ''),
          statusCode: 200,
          data: {
            'count': 3,
            'applications': [],
          },
        ),
      );

      // Act
      final result = await repository.getSentToday('u1');

      // Assert
      expect(result.count, 3);
      expect(result.applications, isEmpty);
    });
  });
}

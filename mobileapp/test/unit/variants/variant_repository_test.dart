import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:dio/dio.dart';

import 'package:jobhunter/core/network/dio_client.dart';
import 'package:jobhunter/core/network/app_error.dart';
import 'package:jobhunter/features/variants/data/variant_repository.dart';

import 'variant_repository_test.mocks.dart';

@GenerateMocks([DioClient, Dio])
void main() {
  late MockDioClient mockDioClient;
  late MockDio mockDio;
  late VariantRepository repository;

  setUp(() {
    mockDioClient = MockDioClient();
    mockDio = MockDio();
    when(mockDioClient.dio).thenReturn(mockDio);
    repository = VariantRepository(dioClient: mockDioClient);
  });

  group('VariantRepository.fetchApprovalToken', () {
    test('returns token string on success', () async {
      // Arrange
      when(mockDio.get(any)).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: ''),
          statusCode: 200,
          data: {'approval_token': 'tok_abc123'},
        ),
      );

      // Act
      final token = await repository.fetchApprovalToken('v1');

      // Assert
      expect(token, 'tok_abc123');
    });

    test('throws AppError when approval_token field is absent', () async {
      // Arrange — backend returns 200 but without the token field
      when(mockDio.get(any)).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: ''),
          statusCode: 200,
          data: <String, dynamic>{},
        ),
      );

      // Act + Assert — fail-closed: missing token must throw, not silently proceed
      expect(
        () => repository.fetchApprovalToken('v1'),
        throwsA(isA<AppError>()),
      );
    });

    test('throws AppError on 403 (ownership gate)', () async {
      // Arrange
      when(mockDio.get(any)).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: ''),
          response: Response(
            requestOptions: RequestOptions(path: ''),
            statusCode: 403,
            data: {'detail': 'Forbidden'},
          ),
          type: DioExceptionType.badResponse,
          error: AppError.fromStatusCode(403),
        ),
      );

      // Act + Assert
      expect(
        () => repository.fetchApprovalToken('v1'),
        throwsA(isA<AppError>()),
      );
    });
  });

  group('VariantRepository.approve', () {
    test('returns ApproveVariantResponse on success', () async {
      // Arrange
      when(mockDio.post(any, data: anyNamed('data'))).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: ''),
          statusCode: 200,
          data: {'variant_id': 'v1', 'status': 'approved'},
        ),
      );

      // Act
      final result = await repository.approve('v1', 'tok_abc123');

      // Assert
      expect(result.variantId, 'v1');
      expect(result.status, 'approved');
    });

    test('throws AppError on 409 token already used', () async {
      // Arrange
      when(mockDio.post(any, data: anyNamed('data'))).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: ''),
          response: Response(
            requestOptions: RequestOptions(path: ''),
            statusCode: 409,
            data: {'detail': 'Token already used'},
          ),
          type: DioExceptionType.badResponse,
          error: AppError.fromStatusCode(409, body: 'Token already used'),
        ),
      );

      // Act + Assert
      expect(
        () => repository.approve('v1', 'tok_used'),
        throwsA(isA<AppError>()),
      );
    });
  });

  group('VariantRepository.reject', () {
    test('completes without throwing on success', () async {
      // Arrange
      when(mockDio.post(any, data: anyNamed('data'))).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: ''),
          statusCode: 200,
          data: {'status': 'rejected'},
        ),
      );

      // Act + Assert
      await expectLater(
        repository.reject('v1', userFeedback: 'Please improve formatting'),
        completes,
      );
    });
  });
}

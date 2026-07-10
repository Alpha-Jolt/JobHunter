import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:dio/dio.dart';

import 'package:jobhunter/core/network/dio_client.dart';
import 'package:jobhunter/core/network/app_error.dart';
import 'package:jobhunter/features/jobs/data/job_models.dart';
import 'package:jobhunter/features/jobs/data/job_repository.dart';

import 'job_repository_test.mocks.dart';

@GenerateMocks([DioClient, Dio])
void main() {
  late MockDioClient mockDioClient;
  late MockDio mockDio;
  late JobRepository repository;

  setUp(() {
    mockDioClient = MockDioClient();
    mockDio = MockDio();
    when(mockDioClient.dio).thenReturn(mockDio);
    repository = JobRepository(dioClient: mockDioClient);
  });

  group('JobRepository.getLatestJobs', () {
    test('returns JobListResponse on success', () async {
      // Arrange
      when(mockDio.get(any, queryParameters: anyNamed('queryParameters')))
          .thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: ''),
          statusCode: 200,
          data: {
            'jobs': [
              {
                'job_id': 'j1',
                'title': 'Flutter Developer',
                'company_name': 'Acme',
                'location': 'Remote',
                'email_trust': 'verified',
                'status': 'raw',
              }
            ],
            'total': 1,
            'page': 1,
            'page_size': 20,
          },
        ),
      );

      // Act
      final result = await repository.getLatestJobs();

      // Assert
      expect(result.jobs.length, 1);
      expect(result.jobs.first.jobId, 'j1');
      expect(result.total, 1);
    });

    test('passes filter query params correctly', () async {
      // Arrange
      when(mockDio.get(any, queryParameters: anyNamed('queryParameters')))
          .thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: ''),
          statusCode: 200,
          data: {'jobs': [], 'total': 0, 'page': 1, 'page_size': 20},
        ),
      );
      const filters = JobFilters(remoteType: 'remote', emailTrust: 'verified');

      // Act
      await repository.getLatestJobs(filters: filters);

      // Assert — verify filter params were passed
      final captured = verify(
        mockDio.get(
          any,
          queryParameters: captureAnyNamed('queryParameters'),
        ),
      ).captured.first as Map<String, dynamic>;

      expect(captured['remote_type'], 'remote');
      expect(captured['email_trust'], 'verified');
    });

    test('throws AppError on network failure', () async {
      // Arrange
      when(mockDio.get(any, queryParameters: anyNamed('queryParameters')))
          .thenThrow(
        DioException(
          requestOptions: RequestOptions(path: ''),
          type: DioExceptionType.connectionError,
          error: AppError.networkUnavailable(),
        ),
      );

      // Act + Assert
      expect(
        () => repository.getLatestJobs(),
        throwsA(isA<AppError>()),
      );
    });
  });

  group('JobFilters.toQueryParams', () {
    test('empty filters produce no query params', () {
      // Arrange + Act
      final params = JobFilters.empty.toQueryParams();

      // Assert
      expect(params, isEmpty);
    });

    test('populated filters produce correct param keys', () {
      // Arrange
      const filters = JobFilters(
        remoteType: 'hybrid',
        jobType: 'fulltime',
        location: 'Bangalore',
        experienceMin: 2,
        experienceMax: 5,
      );

      // Act
      final params = filters.toQueryParams();

      // Assert
      expect(params['remote_type'], 'hybrid');
      expect(params['job_type'], 'fulltime');
      expect(params['location'], 'Bangalore');
      expect(params['experience_min'], 2);
      expect(params['experience_max'], 5);
    });

    test('hasAnyFilter returns false for empty filters', () {
      expect(JobFilters.empty.hasAnyFilter, isFalse);
    });

    test('hasAnyFilter returns true when any field is set', () {
      expect(const JobFilters(remoteType: 'remote').hasAnyFilter, isTrue);
    });
  });
}

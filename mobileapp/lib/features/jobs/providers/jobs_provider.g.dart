// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'jobs_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(jobRepository)
final jobRepositoryProvider = JobRepositoryProvider._();

final class JobRepositoryProvider
    extends $FunctionalProvider<JobRepository, JobRepository, JobRepository>
    with $Provider<JobRepository> {
  JobRepositoryProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'jobRepositoryProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$jobRepositoryHash();

  @$internal
  @override
  $ProviderElement<JobRepository> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  JobRepository create(Ref ref) {
    return jobRepository(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(JobRepository value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<JobRepository>(value),
    );
  }
}

String _$jobRepositoryHash() => r'3ed8159b6553a0026e14dafda6899ddc58b52e78';

@ProviderFor(JobListNotifier)
final jobListProvider = JobListNotifierProvider._();

final class JobListNotifierProvider
    extends $NotifierProvider<JobListNotifier, JobListState> {
  JobListNotifierProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'jobListProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$jobListNotifierHash();

  @$internal
  @override
  JobListNotifier create() => JobListNotifier();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(JobListState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<JobListState>(value),
    );
  }
}

String _$jobListNotifierHash() => r'800925520a9265e5600d9a1a0c2b04ca2d7dbb4d';

abstract class _$JobListNotifier extends $Notifier<JobListState> {
  JobListState build();
  @$mustCallSuper
  @override
  WhenComplete runBuild() {
    final ref = this.ref as $Ref<JobListState, JobListState>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<JobListState, JobListState>,
              JobListState,
              Object?,
              Object?
            >;
    return element.handleCreate(ref, build);
  }
}

@ProviderFor(jobCounts)
final jobCountsProvider = JobCountsProvider._();

final class JobCountsProvider
    extends
        $FunctionalProvider<
          AsyncValue<JobCountsResponse>,
          JobCountsResponse,
          FutureOr<JobCountsResponse>
        >
    with
        $FutureModifier<JobCountsResponse>,
        $FutureProvider<JobCountsResponse> {
  JobCountsProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'jobCountsProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$jobCountsHash();

  @$internal
  @override
  $FutureProviderElement<JobCountsResponse> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<JobCountsResponse> create(Ref ref) {
    return jobCounts(ref);
  }
}

String _$jobCountsHash() => r'2c1f2c9b11c66e78ac4856b9ca5838c7cca87ea7';

// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'resume_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(resumeRepository)
final resumeRepositoryProvider = ResumeRepositoryProvider._();

final class ResumeRepositoryProvider
    extends
        $FunctionalProvider<
          ResumeRepository,
          ResumeRepository,
          ResumeRepository
        >
    with $Provider<ResumeRepository> {
  ResumeRepositoryProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'resumeRepositoryProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$resumeRepositoryHash();

  @$internal
  @override
  $ProviderElement<ResumeRepository> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  ResumeRepository create(Ref ref) {
    return resumeRepository(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(ResumeRepository value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<ResumeRepository>(value),
    );
  }
}

String _$resumeRepositoryHash() => r'5769d8a0400a45e32d5ff1173df29ac1b4a49f27';

/// Holds the most recently uploaded [MasterResume] for the session.
/// VariantGenerationScreen reads `filePath` from this to populate
/// the `resume_file_path` field required by POST /api/ai/generate.

@ProviderFor(MasterResumeNotifier)
final masterResumeProvider = MasterResumeNotifierProvider._();

/// Holds the most recently uploaded [MasterResume] for the session.
/// VariantGenerationScreen reads `filePath` from this to populate
/// the `resume_file_path` field required by POST /api/ai/generate.
final class MasterResumeNotifierProvider
    extends $NotifierProvider<MasterResumeNotifier, MasterResume?> {
  /// Holds the most recently uploaded [MasterResume] for the session.
  /// VariantGenerationScreen reads `filePath` from this to populate
  /// the `resume_file_path` field required by POST /api/ai/generate.
  MasterResumeNotifierProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'masterResumeProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$masterResumeNotifierHash();

  @$internal
  @override
  MasterResumeNotifier create() => MasterResumeNotifier();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(MasterResume? value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<MasterResume?>(value),
    );
  }
}

String _$masterResumeNotifierHash() =>
    r'e6e423cd0f71d140ab0ee9cb337dcf7d79d7cfb8';

/// Holds the most recently uploaded [MasterResume] for the session.
/// VariantGenerationScreen reads `filePath` from this to populate
/// the `resume_file_path` field required by POST /api/ai/generate.

abstract class _$MasterResumeNotifier extends $Notifier<MasterResume?> {
  MasterResume? build();
  @$mustCallSuper
  @override
  WhenComplete runBuild() {
    final ref = this.ref as $Ref<MasterResume?, MasterResume?>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<MasterResume?, MasterResume?>,
              MasterResume?,
              Object?,
              Object?
            >;
    return element.handleCreate(ref, build);
  }
}

@ProviderFor(ResumeUploadNotifier)
final resumeUploadProvider = ResumeUploadNotifierProvider._();

final class ResumeUploadNotifierProvider
    extends $NotifierProvider<ResumeUploadNotifier, ResumeUploadState> {
  ResumeUploadNotifierProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'resumeUploadProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$resumeUploadNotifierHash();

  @$internal
  @override
  ResumeUploadNotifier create() => ResumeUploadNotifier();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(ResumeUploadState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<ResumeUploadState>(value),
    );
  }
}

String _$resumeUploadNotifierHash() =>
    r'70dce7e5e3373d16625039792d1a05b1087a7201';

abstract class _$ResumeUploadNotifier extends $Notifier<ResumeUploadState> {
  ResumeUploadState build();
  @$mustCallSuper
  @override
  WhenComplete runBuild() {
    final ref = this.ref as $Ref<ResumeUploadState, ResumeUploadState>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<ResumeUploadState, ResumeUploadState>,
              ResumeUploadState,
              Object?,
              Object?
            >;
    return element.handleCreate(ref, build);
  }
}

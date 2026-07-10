// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'applications_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(applicationRepository)
final applicationRepositoryProvider = ApplicationRepositoryProvider._();

final class ApplicationRepositoryProvider
    extends
        $FunctionalProvider<
          ApplicationRepository,
          ApplicationRepository,
          ApplicationRepository
        >
    with $Provider<ApplicationRepository> {
  ApplicationRepositoryProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'applicationRepositoryProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$applicationRepositoryHash();

  @$internal
  @override
  $ProviderElement<ApplicationRepository> $createElement(
    $ProviderPointer pointer,
  ) => $ProviderElement(pointer);

  @override
  ApplicationRepository create(Ref ref) {
    return applicationRepository(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(ApplicationRepository value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<ApplicationRepository>(value),
    );
  }
}

String _$applicationRepositoryHash() =>
    r'2f0ffec38fb0960ae9bdcbde61f81d0cf86ed05b';

@ProviderFor(ApplicationListNotifier)
final applicationListProvider = ApplicationListNotifierProvider._();

final class ApplicationListNotifierProvider
    extends $AsyncNotifierProvider<ApplicationListNotifier, SentTodayResponse> {
  ApplicationListNotifierProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'applicationListProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$applicationListNotifierHash();

  @$internal
  @override
  ApplicationListNotifier create() => ApplicationListNotifier();
}

String _$applicationListNotifierHash() =>
    r'5ec3744e0d9bd6a48593fbfa359cdfbb03283a9c';

abstract class _$ApplicationListNotifier
    extends $AsyncNotifier<SentTodayResponse> {
  FutureOr<SentTodayResponse> build();
  @$mustCallSuper
  @override
  WhenComplete runBuild() {
    final ref =
        this.ref as $Ref<AsyncValue<SentTodayResponse>, SentTodayResponse>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<SentTodayResponse>, SentTodayResponse>,
              AsyncValue<SentTodayResponse>,
              Object?,
              Object?
            >;
    return element.handleCreate(ref, build);
  }
}

@ProviderFor(applicationStatus)
final applicationStatusProvider = ApplicationStatusFamily._();

final class ApplicationStatusProvider
    extends
        $FunctionalProvider<
          AsyncValue<ApplicationStatus>,
          ApplicationStatus,
          FutureOr<ApplicationStatus>
        >
    with
        $FutureModifier<ApplicationStatus>,
        $FutureProvider<ApplicationStatus> {
  ApplicationStatusProvider._({
    required ApplicationStatusFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'applicationStatusProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$applicationStatusHash();

  @override
  String toString() {
    return r'applicationStatusProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<ApplicationStatus> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<ApplicationStatus> create(Ref ref) {
    final argument = this.argument as String;
    return applicationStatus(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is ApplicationStatusProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$applicationStatusHash() => r'b88ee59997d119efaeedb72d77ea8230e7d06c79';

final class ApplicationStatusFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<ApplicationStatus>, String> {
  ApplicationStatusFamily._()
    : super(
        retry: null,
        name: r'applicationStatusProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  ApplicationStatusProvider call(String applicationId) =>
      ApplicationStatusProvider._(argument: applicationId, from: this);

  @override
  String toString() => r'applicationStatusProvider';
}

@ProviderFor(SendApplicationNotifier)
final sendApplicationProvider = SendApplicationNotifierProvider._();

final class SendApplicationNotifierProvider
    extends $NotifierProvider<SendApplicationNotifier, SendApplicationState> {
  SendApplicationNotifierProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'sendApplicationProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$sendApplicationNotifierHash();

  @$internal
  @override
  SendApplicationNotifier create() => SendApplicationNotifier();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(SendApplicationState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<SendApplicationState>(value),
    );
  }
}

String _$sendApplicationNotifierHash() =>
    r'92d5ca3ba14bf33e387e6a7379731d287316c744';

abstract class _$SendApplicationNotifier
    extends $Notifier<SendApplicationState> {
  SendApplicationState build();
  @$mustCallSuper
  @override
  WhenComplete runBuild() {
    final ref = this.ref as $Ref<SendApplicationState, SendApplicationState>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<SendApplicationState, SendApplicationState>,
              SendApplicationState,
              Object?,
              Object?
            >;
    return element.handleCreate(ref, build);
  }
}

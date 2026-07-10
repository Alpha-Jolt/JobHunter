// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'variants_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(variantRepository)
final variantRepositoryProvider = VariantRepositoryProvider._();

final class VariantRepositoryProvider
    extends
        $FunctionalProvider<
          VariantRepository,
          VariantRepository,
          VariantRepository
        >
    with $Provider<VariantRepository> {
  VariantRepositoryProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'variantRepositoryProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$variantRepositoryHash();

  @$internal
  @override
  $ProviderElement<VariantRepository> $createElement(
    $ProviderPointer pointer,
  ) => $ProviderElement(pointer);

  @override
  VariantRepository create(Ref ref) {
    return variantRepository(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(VariantRepository value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<VariantRepository>(value),
    );
  }
}

String _$variantRepositoryHash() => r'8cb1be77fed3fe3707e987f987063a108de507c4';

@ProviderFor(VariantListNotifier)
final variantListProvider = VariantListNotifierProvider._();

final class VariantListNotifierProvider
    extends
        $AsyncNotifierProvider<VariantListNotifier, PendingVariantsResponse> {
  VariantListNotifierProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'variantListProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$variantListNotifierHash();

  @$internal
  @override
  VariantListNotifier create() => VariantListNotifier();
}

String _$variantListNotifierHash() =>
    r'fb92808ed3c4e9813239efa7ac6b8b93f97ba945';

abstract class _$VariantListNotifier
    extends $AsyncNotifier<PendingVariantsResponse> {
  FutureOr<PendingVariantsResponse> build();
  @$mustCallSuper
  @override
  WhenComplete runBuild() {
    final ref =
        this.ref
            as $Ref<
              AsyncValue<PendingVariantsResponse>,
              PendingVariantsResponse
            >;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<
                AsyncValue<PendingVariantsResponse>,
                PendingVariantsResponse
              >,
              AsyncValue<PendingVariantsResponse>,
              Object?,
              Object?
            >;
    return element.handleCreate(ref, build);
  }
}

@ProviderFor(variantPreview)
final variantPreviewProvider = VariantPreviewFamily._();

final class VariantPreviewProvider
    extends
        $FunctionalProvider<
          AsyncValue<VariantPreview>,
          VariantPreview,
          FutureOr<VariantPreview>
        >
    with $FutureModifier<VariantPreview>, $FutureProvider<VariantPreview> {
  VariantPreviewProvider._({
    required VariantPreviewFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'variantPreviewProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$variantPreviewHash();

  @override
  String toString() {
    return r'variantPreviewProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<VariantPreview> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<VariantPreview> create(Ref ref) {
    final argument = this.argument as String;
    return variantPreview(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is VariantPreviewProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$variantPreviewHash() => r'3dd44594381519d45cd2a57104ffdc7e6b3098bc';

final class VariantPreviewFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<VariantPreview>, String> {
  VariantPreviewFamily._()
    : super(
        retry: null,
        name: r'variantPreviewProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  VariantPreviewProvider call(String variantId) =>
      VariantPreviewProvider._(argument: variantId, from: this);

  @override
  String toString() => r'variantPreviewProvider';
}

@ProviderFor(VariantGenerationNotifier)
final variantGenerationProvider = VariantGenerationNotifierProvider._();

final class VariantGenerationNotifierProvider
    extends $NotifierProvider<VariantGenerationNotifier, GenerationState> {
  VariantGenerationNotifierProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'variantGenerationProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$variantGenerationNotifierHash();

  @$internal
  @override
  VariantGenerationNotifier create() => VariantGenerationNotifier();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(GenerationState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<GenerationState>(value),
    );
  }
}

String _$variantGenerationNotifierHash() =>
    r'd33283e1884b8f6cab4e1c8b7c2c9cd62b801e41';

abstract class _$VariantGenerationNotifier extends $Notifier<GenerationState> {
  GenerationState build();
  @$mustCallSuper
  @override
  WhenComplete runBuild() {
    final ref = this.ref as $Ref<GenerationState, GenerationState>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<GenerationState, GenerationState>,
              GenerationState,
              Object?,
              Object?
            >;
    return element.handleCreate(ref, build);
  }
}

@ProviderFor(ApprovalFlowNotifier)
final approvalFlowProvider = ApprovalFlowNotifierProvider._();

final class ApprovalFlowNotifierProvider
    extends $NotifierProvider<ApprovalFlowNotifier, ApprovalFlowState> {
  ApprovalFlowNotifierProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'approvalFlowProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$approvalFlowNotifierHash();

  @$internal
  @override
  ApprovalFlowNotifier create() => ApprovalFlowNotifier();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(ApprovalFlowState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<ApprovalFlowState>(value),
    );
  }
}

String _$approvalFlowNotifierHash() =>
    r'987f25704ae65106f40270a06e907d3f28a1da89';

abstract class _$ApprovalFlowNotifier extends $Notifier<ApprovalFlowState> {
  ApprovalFlowState build();
  @$mustCallSuper
  @override
  WhenComplete runBuild() {
    final ref = this.ref as $Ref<ApprovalFlowState, ApprovalFlowState>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<ApprovalFlowState, ApprovalFlowState>,
              ApprovalFlowState,
              Object?,
              Object?
            >;
    return element.handleCreate(ref, build);
  }
}

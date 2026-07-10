import 'package:freezed_annotation/freezed_annotation.dart';

part 'variant_models.freezed.dart';
part 'variant_models.g.dart';

// ── Variant record ────────────────────────────────────────────────────────────

@freezed
abstract class VariantRecord with _$VariantRecord {
  const factory VariantRecord({
    @JsonKey(name: 'variant_id') required String variantId,
    @JsonKey(name: 'user_id') required String userId,
    @JsonKey(name: 'job_id') required String jobId,
    @JsonKey(name: 'master_resume_id') required String masterResumeId,
    @JsonKey(name: 'pdf_key') String? pdfKey,
    @JsonKey(name: 'docx_key') String? docxKey,
    @JsonKey(name: 'cover_letter_key') String? coverLetterKey,
    @JsonKey(name: 'approval_status') @Default('pending') String approvalStatus,
    @JsonKey(name: 'approval_token') String? approvalToken,
    @JsonKey(name: 'approved_at') DateTime? approvedAt,
    @JsonKey(name: 'created_at') DateTime? createdAt,
    @JsonKey(name: 'job_title') String? jobTitle,
    @JsonKey(name: 'company_name') String? companyName,
  }) = _VariantRecord;

  factory VariantRecord.fromJson(Map<String, dynamic> json) =>
      _$VariantRecordFromJson(json);
}

// ── Pending variants response ─────────────────────────────────────────────────

@freezed
abstract class PendingVariantsResponse with _$PendingVariantsResponse {
  const factory PendingVariantsResponse({
    required List<VariantRecord> variants,
    required int total,
  }) = _PendingVariantsResponse;

  factory PendingVariantsResponse.fromJson(Map<String, dynamic> json) =>
      _$PendingVariantsResponseFromJson(json);
}

// ── Variant preview (curated content + gaps) ─────────────────────────────────

@freezed
abstract class VariantPreview with _$VariantPreview {
  const factory VariantPreview({
    @JsonKey(name: 'variant_id') required String variantId,
    @JsonKey(name: 'curated_resume') required Map<String, dynamic> curatedResume,
    @JsonKey(name: 'gaps_identified') @Default([]) List<String> gapsIdentified,
    @JsonKey(name: 'match_score') int? matchScore,
    @JsonKey(name: 'approval_status') @Default('pending') String approvalStatus,
  }) = _VariantPreview;

  factory VariantPreview.fromJson(Map<String, dynamic> json) =>
      _$VariantPreviewFromJson(json);
}

// ── Generate request ──────────────────────────────────────────────────────────

@freezed
abstract class GenerateVariantRequest with _$GenerateVariantRequest {
  const factory GenerateVariantRequest({
    @JsonKey(name: 'user_id') required String userId,
    @JsonKey(name: 'job_id') required String jobId,
    @JsonKey(name: 'resume_file_path') required String resumeFilePath,
  }) = _GenerateVariantRequest;

  factory GenerateVariantRequest.fromJson(Map<String, dynamic> json) =>
      _$GenerateVariantRequestFromJson(json);
}

// ── Approve / reject responses ────────────────────────────────────────────────

@freezed
abstract class ApproveVariantResponse with _$ApproveVariantResponse {
  const factory ApproveVariantResponse({
    @JsonKey(name: 'variant_id') required String variantId,
    required String status,
    String? message,
  }) = _ApproveVariantResponse;

  factory ApproveVariantResponse.fromJson(Map<String, dynamic> json) =>
      _$ApproveVariantResponseFromJson(json);
}

@freezed
abstract class RejectVariantRequest with _$RejectVariantRequest {
  const factory RejectVariantRequest({
    @JsonKey(name: 'user_feedback') String? userFeedback,
  }) = _RejectVariantRequest;

  factory RejectVariantRequest.fromJson(Map<String, dynamic> json) =>
      _$RejectVariantRequestFromJson(json);
}

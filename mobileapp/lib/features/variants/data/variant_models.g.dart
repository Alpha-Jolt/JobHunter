// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'variant_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_VariantRecord _$VariantRecordFromJson(Map<String, dynamic> json) =>
    _VariantRecord(
      variantId: json['variant_id'] as String,
      userId: json['user_id'] as String,
      jobId: json['job_id'] as String,
      masterResumeId: json['master_resume_id'] as String,
      pdfKey: json['pdf_key'] as String?,
      docxKey: json['docx_key'] as String?,
      coverLetterKey: json['cover_letter_key'] as String?,
      approvalStatus: json['approval_status'] as String? ?? 'pending',
      approvalToken: json['approval_token'] as String?,
      approvedAt: json['approved_at'] == null
          ? null
          : DateTime.parse(json['approved_at'] as String),
      createdAt: json['created_at'] == null
          ? null
          : DateTime.parse(json['created_at'] as String),
      jobTitle: json['job_title'] as String?,
      companyName: json['company_name'] as String?,
    );

Map<String, dynamic> _$VariantRecordToJson(_VariantRecord instance) =>
    <String, dynamic>{
      'variant_id': instance.variantId,
      'user_id': instance.userId,
      'job_id': instance.jobId,
      'master_resume_id': instance.masterResumeId,
      'pdf_key': instance.pdfKey,
      'docx_key': instance.docxKey,
      'cover_letter_key': instance.coverLetterKey,
      'approval_status': instance.approvalStatus,
      'approval_token': instance.approvalToken,
      'approved_at': instance.approvedAt?.toIso8601String(),
      'created_at': instance.createdAt?.toIso8601String(),
      'job_title': instance.jobTitle,
      'company_name': instance.companyName,
    };

_PendingVariantsResponse _$PendingVariantsResponseFromJson(
  Map<String, dynamic> json,
) => _PendingVariantsResponse(
  variants: (json['variants'] as List<dynamic>)
      .map((e) => VariantRecord.fromJson(e as Map<String, dynamic>))
      .toList(),
  total: (json['total'] as num).toInt(),
);

Map<String, dynamic> _$PendingVariantsResponseToJson(
  _PendingVariantsResponse instance,
) => <String, dynamic>{'variants': instance.variants, 'total': instance.total};

_VariantPreview _$VariantPreviewFromJson(Map<String, dynamic> json) =>
    _VariantPreview(
      variantId: json['variant_id'] as String,
      curatedResume: json['curated_resume'] as Map<String, dynamic>,
      gapsIdentified:
          (json['gaps_identified'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      matchScore: (json['match_score'] as num?)?.toInt(),
      approvalStatus: json['approval_status'] as String? ?? 'pending',
    );

Map<String, dynamic> _$VariantPreviewToJson(_VariantPreview instance) =>
    <String, dynamic>{
      'variant_id': instance.variantId,
      'curated_resume': instance.curatedResume,
      'gaps_identified': instance.gapsIdentified,
      'match_score': instance.matchScore,
      'approval_status': instance.approvalStatus,
    };

_GenerateVariantRequest _$GenerateVariantRequestFromJson(
  Map<String, dynamic> json,
) => _GenerateVariantRequest(
  userId: json['user_id'] as String,
  jobId: json['job_id'] as String,
  resumeFilePath: json['resume_file_path'] as String,
);

Map<String, dynamic> _$GenerateVariantRequestToJson(
  _GenerateVariantRequest instance,
) => <String, dynamic>{
  'user_id': instance.userId,
  'job_id': instance.jobId,
  'resume_file_path': instance.resumeFilePath,
};

_ApproveVariantResponse _$ApproveVariantResponseFromJson(
  Map<String, dynamic> json,
) => _ApproveVariantResponse(
  variantId: json['variant_id'] as String,
  status: json['status'] as String,
  message: json['message'] as String?,
);

Map<String, dynamic> _$ApproveVariantResponseToJson(
  _ApproveVariantResponse instance,
) => <String, dynamic>{
  'variant_id': instance.variantId,
  'status': instance.status,
  'message': instance.message,
};

_RejectVariantRequest _$RejectVariantRequestFromJson(
  Map<String, dynamic> json,
) => _RejectVariantRequest(userFeedback: json['user_feedback'] as String?);

Map<String, dynamic> _$RejectVariantRequestToJson(
  _RejectVariantRequest instance,
) => <String, dynamic>{'user_feedback': instance.userFeedback};

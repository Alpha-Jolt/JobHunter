// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'variant_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$VariantRecord {

@JsonKey(name: 'variant_id') String get variantId;@JsonKey(name: 'user_id') String get userId;@JsonKey(name: 'job_id') String get jobId;@JsonKey(name: 'master_resume_id') String get masterResumeId;@JsonKey(name: 'pdf_key') String? get pdfKey;@JsonKey(name: 'docx_key') String? get docxKey;@JsonKey(name: 'cover_letter_key') String? get coverLetterKey;@JsonKey(name: 'approval_status') String get approvalStatus;@JsonKey(name: 'approval_token') String? get approvalToken;@JsonKey(name: 'approved_at') DateTime? get approvedAt;@JsonKey(name: 'created_at') DateTime? get createdAt;@JsonKey(name: 'job_title') String? get jobTitle;@JsonKey(name: 'company_name') String? get companyName;
/// Create a copy of VariantRecord
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$VariantRecordCopyWith<VariantRecord> get copyWith => _$VariantRecordCopyWithImpl<VariantRecord>(this as VariantRecord, _$identity);

  /// Serializes this VariantRecord to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is VariantRecord&&(identical(other.variantId, variantId) || other.variantId == variantId)&&(identical(other.userId, userId) || other.userId == userId)&&(identical(other.jobId, jobId) || other.jobId == jobId)&&(identical(other.masterResumeId, masterResumeId) || other.masterResumeId == masterResumeId)&&(identical(other.pdfKey, pdfKey) || other.pdfKey == pdfKey)&&(identical(other.docxKey, docxKey) || other.docxKey == docxKey)&&(identical(other.coverLetterKey, coverLetterKey) || other.coverLetterKey == coverLetterKey)&&(identical(other.approvalStatus, approvalStatus) || other.approvalStatus == approvalStatus)&&(identical(other.approvalToken, approvalToken) || other.approvalToken == approvalToken)&&(identical(other.approvedAt, approvedAt) || other.approvedAt == approvedAt)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.jobTitle, jobTitle) || other.jobTitle == jobTitle)&&(identical(other.companyName, companyName) || other.companyName == companyName));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,variantId,userId,jobId,masterResumeId,pdfKey,docxKey,coverLetterKey,approvalStatus,approvalToken,approvedAt,createdAt,jobTitle,companyName);

@override
String toString() {
  return 'VariantRecord(variantId: $variantId, userId: $userId, jobId: $jobId, masterResumeId: $masterResumeId, pdfKey: $pdfKey, docxKey: $docxKey, coverLetterKey: $coverLetterKey, approvalStatus: $approvalStatus, approvalToken: $approvalToken, approvedAt: $approvedAt, createdAt: $createdAt, jobTitle: $jobTitle, companyName: $companyName)';
}


}

/// @nodoc
abstract mixin class $VariantRecordCopyWith<$Res>  {
  factory $VariantRecordCopyWith(VariantRecord value, $Res Function(VariantRecord) _then) = _$VariantRecordCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'variant_id') String variantId,@JsonKey(name: 'user_id') String userId,@JsonKey(name: 'job_id') String jobId,@JsonKey(name: 'master_resume_id') String masterResumeId,@JsonKey(name: 'pdf_key') String? pdfKey,@JsonKey(name: 'docx_key') String? docxKey,@JsonKey(name: 'cover_letter_key') String? coverLetterKey,@JsonKey(name: 'approval_status') String approvalStatus,@JsonKey(name: 'approval_token') String? approvalToken,@JsonKey(name: 'approved_at') DateTime? approvedAt,@JsonKey(name: 'created_at') DateTime? createdAt,@JsonKey(name: 'job_title') String? jobTitle,@JsonKey(name: 'company_name') String? companyName
});




}
/// @nodoc
class _$VariantRecordCopyWithImpl<$Res>
    implements $VariantRecordCopyWith<$Res> {
  _$VariantRecordCopyWithImpl(this._self, this._then);

  final VariantRecord _self;
  final $Res Function(VariantRecord) _then;

/// Create a copy of VariantRecord
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? variantId = null,Object? userId = null,Object? jobId = null,Object? masterResumeId = null,Object? pdfKey = freezed,Object? docxKey = freezed,Object? coverLetterKey = freezed,Object? approvalStatus = null,Object? approvalToken = freezed,Object? approvedAt = freezed,Object? createdAt = freezed,Object? jobTitle = freezed,Object? companyName = freezed,}) {
  return _then(_self.copyWith(
variantId: null == variantId ? _self.variantId : variantId // ignore: cast_nullable_to_non_nullable
as String,userId: null == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String,jobId: null == jobId ? _self.jobId : jobId // ignore: cast_nullable_to_non_nullable
as String,masterResumeId: null == masterResumeId ? _self.masterResumeId : masterResumeId // ignore: cast_nullable_to_non_nullable
as String,pdfKey: freezed == pdfKey ? _self.pdfKey : pdfKey // ignore: cast_nullable_to_non_nullable
as String?,docxKey: freezed == docxKey ? _self.docxKey : docxKey // ignore: cast_nullable_to_non_nullable
as String?,coverLetterKey: freezed == coverLetterKey ? _self.coverLetterKey : coverLetterKey // ignore: cast_nullable_to_non_nullable
as String?,approvalStatus: null == approvalStatus ? _self.approvalStatus : approvalStatus // ignore: cast_nullable_to_non_nullable
as String,approvalToken: freezed == approvalToken ? _self.approvalToken : approvalToken // ignore: cast_nullable_to_non_nullable
as String?,approvedAt: freezed == approvedAt ? _self.approvedAt : approvedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime?,jobTitle: freezed == jobTitle ? _self.jobTitle : jobTitle // ignore: cast_nullable_to_non_nullable
as String?,companyName: freezed == companyName ? _self.companyName : companyName // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [VariantRecord].
extension VariantRecordPatterns on VariantRecord {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _VariantRecord value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _VariantRecord() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _VariantRecord value)  $default,){
final _that = this;
switch (_that) {
case _VariantRecord():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _VariantRecord value)?  $default,){
final _that = this;
switch (_that) {
case _VariantRecord() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'variant_id')  String variantId, @JsonKey(name: 'user_id')  String userId, @JsonKey(name: 'job_id')  String jobId, @JsonKey(name: 'master_resume_id')  String masterResumeId, @JsonKey(name: 'pdf_key')  String? pdfKey, @JsonKey(name: 'docx_key')  String? docxKey, @JsonKey(name: 'cover_letter_key')  String? coverLetterKey, @JsonKey(name: 'approval_status')  String approvalStatus, @JsonKey(name: 'approval_token')  String? approvalToken, @JsonKey(name: 'approved_at')  DateTime? approvedAt, @JsonKey(name: 'created_at')  DateTime? createdAt, @JsonKey(name: 'job_title')  String? jobTitle, @JsonKey(name: 'company_name')  String? companyName)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _VariantRecord() when $default != null:
return $default(_that.variantId,_that.userId,_that.jobId,_that.masterResumeId,_that.pdfKey,_that.docxKey,_that.coverLetterKey,_that.approvalStatus,_that.approvalToken,_that.approvedAt,_that.createdAt,_that.jobTitle,_that.companyName);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'variant_id')  String variantId, @JsonKey(name: 'user_id')  String userId, @JsonKey(name: 'job_id')  String jobId, @JsonKey(name: 'master_resume_id')  String masterResumeId, @JsonKey(name: 'pdf_key')  String? pdfKey, @JsonKey(name: 'docx_key')  String? docxKey, @JsonKey(name: 'cover_letter_key')  String? coverLetterKey, @JsonKey(name: 'approval_status')  String approvalStatus, @JsonKey(name: 'approval_token')  String? approvalToken, @JsonKey(name: 'approved_at')  DateTime? approvedAt, @JsonKey(name: 'created_at')  DateTime? createdAt, @JsonKey(name: 'job_title')  String? jobTitle, @JsonKey(name: 'company_name')  String? companyName)  $default,) {final _that = this;
switch (_that) {
case _VariantRecord():
return $default(_that.variantId,_that.userId,_that.jobId,_that.masterResumeId,_that.pdfKey,_that.docxKey,_that.coverLetterKey,_that.approvalStatus,_that.approvalToken,_that.approvedAt,_that.createdAt,_that.jobTitle,_that.companyName);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'variant_id')  String variantId, @JsonKey(name: 'user_id')  String userId, @JsonKey(name: 'job_id')  String jobId, @JsonKey(name: 'master_resume_id')  String masterResumeId, @JsonKey(name: 'pdf_key')  String? pdfKey, @JsonKey(name: 'docx_key')  String? docxKey, @JsonKey(name: 'cover_letter_key')  String? coverLetterKey, @JsonKey(name: 'approval_status')  String approvalStatus, @JsonKey(name: 'approval_token')  String? approvalToken, @JsonKey(name: 'approved_at')  DateTime? approvedAt, @JsonKey(name: 'created_at')  DateTime? createdAt, @JsonKey(name: 'job_title')  String? jobTitle, @JsonKey(name: 'company_name')  String? companyName)?  $default,) {final _that = this;
switch (_that) {
case _VariantRecord() when $default != null:
return $default(_that.variantId,_that.userId,_that.jobId,_that.masterResumeId,_that.pdfKey,_that.docxKey,_that.coverLetterKey,_that.approvalStatus,_that.approvalToken,_that.approvedAt,_that.createdAt,_that.jobTitle,_that.companyName);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _VariantRecord implements VariantRecord {
  const _VariantRecord({@JsonKey(name: 'variant_id') required this.variantId, @JsonKey(name: 'user_id') required this.userId, @JsonKey(name: 'job_id') required this.jobId, @JsonKey(name: 'master_resume_id') required this.masterResumeId, @JsonKey(name: 'pdf_key') this.pdfKey, @JsonKey(name: 'docx_key') this.docxKey, @JsonKey(name: 'cover_letter_key') this.coverLetterKey, @JsonKey(name: 'approval_status') this.approvalStatus = 'pending', @JsonKey(name: 'approval_token') this.approvalToken, @JsonKey(name: 'approved_at') this.approvedAt, @JsonKey(name: 'created_at') this.createdAt, @JsonKey(name: 'job_title') this.jobTitle, @JsonKey(name: 'company_name') this.companyName});
  factory _VariantRecord.fromJson(Map<String, dynamic> json) => _$VariantRecordFromJson(json);

@override@JsonKey(name: 'variant_id') final  String variantId;
@override@JsonKey(name: 'user_id') final  String userId;
@override@JsonKey(name: 'job_id') final  String jobId;
@override@JsonKey(name: 'master_resume_id') final  String masterResumeId;
@override@JsonKey(name: 'pdf_key') final  String? pdfKey;
@override@JsonKey(name: 'docx_key') final  String? docxKey;
@override@JsonKey(name: 'cover_letter_key') final  String? coverLetterKey;
@override@JsonKey(name: 'approval_status') final  String approvalStatus;
@override@JsonKey(name: 'approval_token') final  String? approvalToken;
@override@JsonKey(name: 'approved_at') final  DateTime? approvedAt;
@override@JsonKey(name: 'created_at') final  DateTime? createdAt;
@override@JsonKey(name: 'job_title') final  String? jobTitle;
@override@JsonKey(name: 'company_name') final  String? companyName;

/// Create a copy of VariantRecord
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$VariantRecordCopyWith<_VariantRecord> get copyWith => __$VariantRecordCopyWithImpl<_VariantRecord>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$VariantRecordToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _VariantRecord&&(identical(other.variantId, variantId) || other.variantId == variantId)&&(identical(other.userId, userId) || other.userId == userId)&&(identical(other.jobId, jobId) || other.jobId == jobId)&&(identical(other.masterResumeId, masterResumeId) || other.masterResumeId == masterResumeId)&&(identical(other.pdfKey, pdfKey) || other.pdfKey == pdfKey)&&(identical(other.docxKey, docxKey) || other.docxKey == docxKey)&&(identical(other.coverLetterKey, coverLetterKey) || other.coverLetterKey == coverLetterKey)&&(identical(other.approvalStatus, approvalStatus) || other.approvalStatus == approvalStatus)&&(identical(other.approvalToken, approvalToken) || other.approvalToken == approvalToken)&&(identical(other.approvedAt, approvedAt) || other.approvedAt == approvedAt)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.jobTitle, jobTitle) || other.jobTitle == jobTitle)&&(identical(other.companyName, companyName) || other.companyName == companyName));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,variantId,userId,jobId,masterResumeId,pdfKey,docxKey,coverLetterKey,approvalStatus,approvalToken,approvedAt,createdAt,jobTitle,companyName);

@override
String toString() {
  return 'VariantRecord(variantId: $variantId, userId: $userId, jobId: $jobId, masterResumeId: $masterResumeId, pdfKey: $pdfKey, docxKey: $docxKey, coverLetterKey: $coverLetterKey, approvalStatus: $approvalStatus, approvalToken: $approvalToken, approvedAt: $approvedAt, createdAt: $createdAt, jobTitle: $jobTitle, companyName: $companyName)';
}


}

/// @nodoc
abstract mixin class _$VariantRecordCopyWith<$Res> implements $VariantRecordCopyWith<$Res> {
  factory _$VariantRecordCopyWith(_VariantRecord value, $Res Function(_VariantRecord) _then) = __$VariantRecordCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'variant_id') String variantId,@JsonKey(name: 'user_id') String userId,@JsonKey(name: 'job_id') String jobId,@JsonKey(name: 'master_resume_id') String masterResumeId,@JsonKey(name: 'pdf_key') String? pdfKey,@JsonKey(name: 'docx_key') String? docxKey,@JsonKey(name: 'cover_letter_key') String? coverLetterKey,@JsonKey(name: 'approval_status') String approvalStatus,@JsonKey(name: 'approval_token') String? approvalToken,@JsonKey(name: 'approved_at') DateTime? approvedAt,@JsonKey(name: 'created_at') DateTime? createdAt,@JsonKey(name: 'job_title') String? jobTitle,@JsonKey(name: 'company_name') String? companyName
});




}
/// @nodoc
class __$VariantRecordCopyWithImpl<$Res>
    implements _$VariantRecordCopyWith<$Res> {
  __$VariantRecordCopyWithImpl(this._self, this._then);

  final _VariantRecord _self;
  final $Res Function(_VariantRecord) _then;

/// Create a copy of VariantRecord
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? variantId = null,Object? userId = null,Object? jobId = null,Object? masterResumeId = null,Object? pdfKey = freezed,Object? docxKey = freezed,Object? coverLetterKey = freezed,Object? approvalStatus = null,Object? approvalToken = freezed,Object? approvedAt = freezed,Object? createdAt = freezed,Object? jobTitle = freezed,Object? companyName = freezed,}) {
  return _then(_VariantRecord(
variantId: null == variantId ? _self.variantId : variantId // ignore: cast_nullable_to_non_nullable
as String,userId: null == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String,jobId: null == jobId ? _self.jobId : jobId // ignore: cast_nullable_to_non_nullable
as String,masterResumeId: null == masterResumeId ? _self.masterResumeId : masterResumeId // ignore: cast_nullable_to_non_nullable
as String,pdfKey: freezed == pdfKey ? _self.pdfKey : pdfKey // ignore: cast_nullable_to_non_nullable
as String?,docxKey: freezed == docxKey ? _self.docxKey : docxKey // ignore: cast_nullable_to_non_nullable
as String?,coverLetterKey: freezed == coverLetterKey ? _self.coverLetterKey : coverLetterKey // ignore: cast_nullable_to_non_nullable
as String?,approvalStatus: null == approvalStatus ? _self.approvalStatus : approvalStatus // ignore: cast_nullable_to_non_nullable
as String,approvalToken: freezed == approvalToken ? _self.approvalToken : approvalToken // ignore: cast_nullable_to_non_nullable
as String?,approvedAt: freezed == approvedAt ? _self.approvedAt : approvedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime?,jobTitle: freezed == jobTitle ? _self.jobTitle : jobTitle // ignore: cast_nullable_to_non_nullable
as String?,companyName: freezed == companyName ? _self.companyName : companyName // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$PendingVariantsResponse {

 List<VariantRecord> get variants; int get total;
/// Create a copy of PendingVariantsResponse
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PendingVariantsResponseCopyWith<PendingVariantsResponse> get copyWith => _$PendingVariantsResponseCopyWithImpl<PendingVariantsResponse>(this as PendingVariantsResponse, _$identity);

  /// Serializes this PendingVariantsResponse to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PendingVariantsResponse&&const DeepCollectionEquality().equals(other.variants, variants)&&(identical(other.total, total) || other.total == total));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(variants),total);

@override
String toString() {
  return 'PendingVariantsResponse(variants: $variants, total: $total)';
}


}

/// @nodoc
abstract mixin class $PendingVariantsResponseCopyWith<$Res>  {
  factory $PendingVariantsResponseCopyWith(PendingVariantsResponse value, $Res Function(PendingVariantsResponse) _then) = _$PendingVariantsResponseCopyWithImpl;
@useResult
$Res call({
 List<VariantRecord> variants, int total
});




}
/// @nodoc
class _$PendingVariantsResponseCopyWithImpl<$Res>
    implements $PendingVariantsResponseCopyWith<$Res> {
  _$PendingVariantsResponseCopyWithImpl(this._self, this._then);

  final PendingVariantsResponse _self;
  final $Res Function(PendingVariantsResponse) _then;

/// Create a copy of PendingVariantsResponse
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? variants = null,Object? total = null,}) {
  return _then(_self.copyWith(
variants: null == variants ? _self.variants : variants // ignore: cast_nullable_to_non_nullable
as List<VariantRecord>,total: null == total ? _self.total : total // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [PendingVariantsResponse].
extension PendingVariantsResponsePatterns on PendingVariantsResponse {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PendingVariantsResponse value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PendingVariantsResponse() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PendingVariantsResponse value)  $default,){
final _that = this;
switch (_that) {
case _PendingVariantsResponse():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PendingVariantsResponse value)?  $default,){
final _that = this;
switch (_that) {
case _PendingVariantsResponse() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( List<VariantRecord> variants,  int total)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PendingVariantsResponse() when $default != null:
return $default(_that.variants,_that.total);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( List<VariantRecord> variants,  int total)  $default,) {final _that = this;
switch (_that) {
case _PendingVariantsResponse():
return $default(_that.variants,_that.total);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( List<VariantRecord> variants,  int total)?  $default,) {final _that = this;
switch (_that) {
case _PendingVariantsResponse() when $default != null:
return $default(_that.variants,_that.total);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _PendingVariantsResponse implements PendingVariantsResponse {
  const _PendingVariantsResponse({required final  List<VariantRecord> variants, required this.total}): _variants = variants;
  factory _PendingVariantsResponse.fromJson(Map<String, dynamic> json) => _$PendingVariantsResponseFromJson(json);

 final  List<VariantRecord> _variants;
@override List<VariantRecord> get variants {
  if (_variants is EqualUnmodifiableListView) return _variants;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_variants);
}

@override final  int total;

/// Create a copy of PendingVariantsResponse
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PendingVariantsResponseCopyWith<_PendingVariantsResponse> get copyWith => __$PendingVariantsResponseCopyWithImpl<_PendingVariantsResponse>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PendingVariantsResponseToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _PendingVariantsResponse&&const DeepCollectionEquality().equals(other._variants, _variants)&&(identical(other.total, total) || other.total == total));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_variants),total);

@override
String toString() {
  return 'PendingVariantsResponse(variants: $variants, total: $total)';
}


}

/// @nodoc
abstract mixin class _$PendingVariantsResponseCopyWith<$Res> implements $PendingVariantsResponseCopyWith<$Res> {
  factory _$PendingVariantsResponseCopyWith(_PendingVariantsResponse value, $Res Function(_PendingVariantsResponse) _then) = __$PendingVariantsResponseCopyWithImpl;
@override @useResult
$Res call({
 List<VariantRecord> variants, int total
});




}
/// @nodoc
class __$PendingVariantsResponseCopyWithImpl<$Res>
    implements _$PendingVariantsResponseCopyWith<$Res> {
  __$PendingVariantsResponseCopyWithImpl(this._self, this._then);

  final _PendingVariantsResponse _self;
  final $Res Function(_PendingVariantsResponse) _then;

/// Create a copy of PendingVariantsResponse
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? variants = null,Object? total = null,}) {
  return _then(_PendingVariantsResponse(
variants: null == variants ? _self._variants : variants // ignore: cast_nullable_to_non_nullable
as List<VariantRecord>,total: null == total ? _self.total : total // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$VariantPreview {

@JsonKey(name: 'variant_id') String get variantId;@JsonKey(name: 'curated_resume') Map<String, dynamic> get curatedResume;@JsonKey(name: 'gaps_identified') List<String> get gapsIdentified;@JsonKey(name: 'match_score') int? get matchScore;@JsonKey(name: 'approval_status') String get approvalStatus;
/// Create a copy of VariantPreview
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$VariantPreviewCopyWith<VariantPreview> get copyWith => _$VariantPreviewCopyWithImpl<VariantPreview>(this as VariantPreview, _$identity);

  /// Serializes this VariantPreview to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is VariantPreview&&(identical(other.variantId, variantId) || other.variantId == variantId)&&const DeepCollectionEquality().equals(other.curatedResume, curatedResume)&&const DeepCollectionEquality().equals(other.gapsIdentified, gapsIdentified)&&(identical(other.matchScore, matchScore) || other.matchScore == matchScore)&&(identical(other.approvalStatus, approvalStatus) || other.approvalStatus == approvalStatus));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,variantId,const DeepCollectionEquality().hash(curatedResume),const DeepCollectionEquality().hash(gapsIdentified),matchScore,approvalStatus);

@override
String toString() {
  return 'VariantPreview(variantId: $variantId, curatedResume: $curatedResume, gapsIdentified: $gapsIdentified, matchScore: $matchScore, approvalStatus: $approvalStatus)';
}


}

/// @nodoc
abstract mixin class $VariantPreviewCopyWith<$Res>  {
  factory $VariantPreviewCopyWith(VariantPreview value, $Res Function(VariantPreview) _then) = _$VariantPreviewCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'variant_id') String variantId,@JsonKey(name: 'curated_resume') Map<String, dynamic> curatedResume,@JsonKey(name: 'gaps_identified') List<String> gapsIdentified,@JsonKey(name: 'match_score') int? matchScore,@JsonKey(name: 'approval_status') String approvalStatus
});




}
/// @nodoc
class _$VariantPreviewCopyWithImpl<$Res>
    implements $VariantPreviewCopyWith<$Res> {
  _$VariantPreviewCopyWithImpl(this._self, this._then);

  final VariantPreview _self;
  final $Res Function(VariantPreview) _then;

/// Create a copy of VariantPreview
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? variantId = null,Object? curatedResume = null,Object? gapsIdentified = null,Object? matchScore = freezed,Object? approvalStatus = null,}) {
  return _then(_self.copyWith(
variantId: null == variantId ? _self.variantId : variantId // ignore: cast_nullable_to_non_nullable
as String,curatedResume: null == curatedResume ? _self.curatedResume : curatedResume // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,gapsIdentified: null == gapsIdentified ? _self.gapsIdentified : gapsIdentified // ignore: cast_nullable_to_non_nullable
as List<String>,matchScore: freezed == matchScore ? _self.matchScore : matchScore // ignore: cast_nullable_to_non_nullable
as int?,approvalStatus: null == approvalStatus ? _self.approvalStatus : approvalStatus // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [VariantPreview].
extension VariantPreviewPatterns on VariantPreview {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _VariantPreview value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _VariantPreview() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _VariantPreview value)  $default,){
final _that = this;
switch (_that) {
case _VariantPreview():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _VariantPreview value)?  $default,){
final _that = this;
switch (_that) {
case _VariantPreview() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'variant_id')  String variantId, @JsonKey(name: 'curated_resume')  Map<String, dynamic> curatedResume, @JsonKey(name: 'gaps_identified')  List<String> gapsIdentified, @JsonKey(name: 'match_score')  int? matchScore, @JsonKey(name: 'approval_status')  String approvalStatus)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _VariantPreview() when $default != null:
return $default(_that.variantId,_that.curatedResume,_that.gapsIdentified,_that.matchScore,_that.approvalStatus);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'variant_id')  String variantId, @JsonKey(name: 'curated_resume')  Map<String, dynamic> curatedResume, @JsonKey(name: 'gaps_identified')  List<String> gapsIdentified, @JsonKey(name: 'match_score')  int? matchScore, @JsonKey(name: 'approval_status')  String approvalStatus)  $default,) {final _that = this;
switch (_that) {
case _VariantPreview():
return $default(_that.variantId,_that.curatedResume,_that.gapsIdentified,_that.matchScore,_that.approvalStatus);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'variant_id')  String variantId, @JsonKey(name: 'curated_resume')  Map<String, dynamic> curatedResume, @JsonKey(name: 'gaps_identified')  List<String> gapsIdentified, @JsonKey(name: 'match_score')  int? matchScore, @JsonKey(name: 'approval_status')  String approvalStatus)?  $default,) {final _that = this;
switch (_that) {
case _VariantPreview() when $default != null:
return $default(_that.variantId,_that.curatedResume,_that.gapsIdentified,_that.matchScore,_that.approvalStatus);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _VariantPreview implements VariantPreview {
  const _VariantPreview({@JsonKey(name: 'variant_id') required this.variantId, @JsonKey(name: 'curated_resume') required final  Map<String, dynamic> curatedResume, @JsonKey(name: 'gaps_identified') final  List<String> gapsIdentified = const [], @JsonKey(name: 'match_score') this.matchScore, @JsonKey(name: 'approval_status') this.approvalStatus = 'pending'}): _curatedResume = curatedResume,_gapsIdentified = gapsIdentified;
  factory _VariantPreview.fromJson(Map<String, dynamic> json) => _$VariantPreviewFromJson(json);

@override@JsonKey(name: 'variant_id') final  String variantId;
 final  Map<String, dynamic> _curatedResume;
@override@JsonKey(name: 'curated_resume') Map<String, dynamic> get curatedResume {
  if (_curatedResume is EqualUnmodifiableMapView) return _curatedResume;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_curatedResume);
}

 final  List<String> _gapsIdentified;
@override@JsonKey(name: 'gaps_identified') List<String> get gapsIdentified {
  if (_gapsIdentified is EqualUnmodifiableListView) return _gapsIdentified;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_gapsIdentified);
}

@override@JsonKey(name: 'match_score') final  int? matchScore;
@override@JsonKey(name: 'approval_status') final  String approvalStatus;

/// Create a copy of VariantPreview
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$VariantPreviewCopyWith<_VariantPreview> get copyWith => __$VariantPreviewCopyWithImpl<_VariantPreview>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$VariantPreviewToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _VariantPreview&&(identical(other.variantId, variantId) || other.variantId == variantId)&&const DeepCollectionEquality().equals(other._curatedResume, _curatedResume)&&const DeepCollectionEquality().equals(other._gapsIdentified, _gapsIdentified)&&(identical(other.matchScore, matchScore) || other.matchScore == matchScore)&&(identical(other.approvalStatus, approvalStatus) || other.approvalStatus == approvalStatus));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,variantId,const DeepCollectionEquality().hash(_curatedResume),const DeepCollectionEquality().hash(_gapsIdentified),matchScore,approvalStatus);

@override
String toString() {
  return 'VariantPreview(variantId: $variantId, curatedResume: $curatedResume, gapsIdentified: $gapsIdentified, matchScore: $matchScore, approvalStatus: $approvalStatus)';
}


}

/// @nodoc
abstract mixin class _$VariantPreviewCopyWith<$Res> implements $VariantPreviewCopyWith<$Res> {
  factory _$VariantPreviewCopyWith(_VariantPreview value, $Res Function(_VariantPreview) _then) = __$VariantPreviewCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'variant_id') String variantId,@JsonKey(name: 'curated_resume') Map<String, dynamic> curatedResume,@JsonKey(name: 'gaps_identified') List<String> gapsIdentified,@JsonKey(name: 'match_score') int? matchScore,@JsonKey(name: 'approval_status') String approvalStatus
});




}
/// @nodoc
class __$VariantPreviewCopyWithImpl<$Res>
    implements _$VariantPreviewCopyWith<$Res> {
  __$VariantPreviewCopyWithImpl(this._self, this._then);

  final _VariantPreview _self;
  final $Res Function(_VariantPreview) _then;

/// Create a copy of VariantPreview
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? variantId = null,Object? curatedResume = null,Object? gapsIdentified = null,Object? matchScore = freezed,Object? approvalStatus = null,}) {
  return _then(_VariantPreview(
variantId: null == variantId ? _self.variantId : variantId // ignore: cast_nullable_to_non_nullable
as String,curatedResume: null == curatedResume ? _self._curatedResume : curatedResume // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,gapsIdentified: null == gapsIdentified ? _self._gapsIdentified : gapsIdentified // ignore: cast_nullable_to_non_nullable
as List<String>,matchScore: freezed == matchScore ? _self.matchScore : matchScore // ignore: cast_nullable_to_non_nullable
as int?,approvalStatus: null == approvalStatus ? _self.approvalStatus : approvalStatus // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$GenerateVariantRequest {

@JsonKey(name: 'user_id') String get userId;@JsonKey(name: 'job_id') String get jobId;@JsonKey(name: 'resume_file_path') String get resumeFilePath;
/// Create a copy of GenerateVariantRequest
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$GenerateVariantRequestCopyWith<GenerateVariantRequest> get copyWith => _$GenerateVariantRequestCopyWithImpl<GenerateVariantRequest>(this as GenerateVariantRequest, _$identity);

  /// Serializes this GenerateVariantRequest to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is GenerateVariantRequest&&(identical(other.userId, userId) || other.userId == userId)&&(identical(other.jobId, jobId) || other.jobId == jobId)&&(identical(other.resumeFilePath, resumeFilePath) || other.resumeFilePath == resumeFilePath));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,userId,jobId,resumeFilePath);

@override
String toString() {
  return 'GenerateVariantRequest(userId: $userId, jobId: $jobId, resumeFilePath: $resumeFilePath)';
}


}

/// @nodoc
abstract mixin class $GenerateVariantRequestCopyWith<$Res>  {
  factory $GenerateVariantRequestCopyWith(GenerateVariantRequest value, $Res Function(GenerateVariantRequest) _then) = _$GenerateVariantRequestCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'user_id') String userId,@JsonKey(name: 'job_id') String jobId,@JsonKey(name: 'resume_file_path') String resumeFilePath
});




}
/// @nodoc
class _$GenerateVariantRequestCopyWithImpl<$Res>
    implements $GenerateVariantRequestCopyWith<$Res> {
  _$GenerateVariantRequestCopyWithImpl(this._self, this._then);

  final GenerateVariantRequest _self;
  final $Res Function(GenerateVariantRequest) _then;

/// Create a copy of GenerateVariantRequest
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? userId = null,Object? jobId = null,Object? resumeFilePath = null,}) {
  return _then(_self.copyWith(
userId: null == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String,jobId: null == jobId ? _self.jobId : jobId // ignore: cast_nullable_to_non_nullable
as String,resumeFilePath: null == resumeFilePath ? _self.resumeFilePath : resumeFilePath // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [GenerateVariantRequest].
extension GenerateVariantRequestPatterns on GenerateVariantRequest {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _GenerateVariantRequest value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _GenerateVariantRequest() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _GenerateVariantRequest value)  $default,){
final _that = this;
switch (_that) {
case _GenerateVariantRequest():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _GenerateVariantRequest value)?  $default,){
final _that = this;
switch (_that) {
case _GenerateVariantRequest() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'user_id')  String userId, @JsonKey(name: 'job_id')  String jobId, @JsonKey(name: 'resume_file_path')  String resumeFilePath)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _GenerateVariantRequest() when $default != null:
return $default(_that.userId,_that.jobId,_that.resumeFilePath);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'user_id')  String userId, @JsonKey(name: 'job_id')  String jobId, @JsonKey(name: 'resume_file_path')  String resumeFilePath)  $default,) {final _that = this;
switch (_that) {
case _GenerateVariantRequest():
return $default(_that.userId,_that.jobId,_that.resumeFilePath);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'user_id')  String userId, @JsonKey(name: 'job_id')  String jobId, @JsonKey(name: 'resume_file_path')  String resumeFilePath)?  $default,) {final _that = this;
switch (_that) {
case _GenerateVariantRequest() when $default != null:
return $default(_that.userId,_that.jobId,_that.resumeFilePath);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _GenerateVariantRequest implements GenerateVariantRequest {
  const _GenerateVariantRequest({@JsonKey(name: 'user_id') required this.userId, @JsonKey(name: 'job_id') required this.jobId, @JsonKey(name: 'resume_file_path') required this.resumeFilePath});
  factory _GenerateVariantRequest.fromJson(Map<String, dynamic> json) => _$GenerateVariantRequestFromJson(json);

@override@JsonKey(name: 'user_id') final  String userId;
@override@JsonKey(name: 'job_id') final  String jobId;
@override@JsonKey(name: 'resume_file_path') final  String resumeFilePath;

/// Create a copy of GenerateVariantRequest
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$GenerateVariantRequestCopyWith<_GenerateVariantRequest> get copyWith => __$GenerateVariantRequestCopyWithImpl<_GenerateVariantRequest>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$GenerateVariantRequestToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _GenerateVariantRequest&&(identical(other.userId, userId) || other.userId == userId)&&(identical(other.jobId, jobId) || other.jobId == jobId)&&(identical(other.resumeFilePath, resumeFilePath) || other.resumeFilePath == resumeFilePath));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,userId,jobId,resumeFilePath);

@override
String toString() {
  return 'GenerateVariantRequest(userId: $userId, jobId: $jobId, resumeFilePath: $resumeFilePath)';
}


}

/// @nodoc
abstract mixin class _$GenerateVariantRequestCopyWith<$Res> implements $GenerateVariantRequestCopyWith<$Res> {
  factory _$GenerateVariantRequestCopyWith(_GenerateVariantRequest value, $Res Function(_GenerateVariantRequest) _then) = __$GenerateVariantRequestCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'user_id') String userId,@JsonKey(name: 'job_id') String jobId,@JsonKey(name: 'resume_file_path') String resumeFilePath
});




}
/// @nodoc
class __$GenerateVariantRequestCopyWithImpl<$Res>
    implements _$GenerateVariantRequestCopyWith<$Res> {
  __$GenerateVariantRequestCopyWithImpl(this._self, this._then);

  final _GenerateVariantRequest _self;
  final $Res Function(_GenerateVariantRequest) _then;

/// Create a copy of GenerateVariantRequest
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? userId = null,Object? jobId = null,Object? resumeFilePath = null,}) {
  return _then(_GenerateVariantRequest(
userId: null == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String,jobId: null == jobId ? _self.jobId : jobId // ignore: cast_nullable_to_non_nullable
as String,resumeFilePath: null == resumeFilePath ? _self.resumeFilePath : resumeFilePath // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$ApproveVariantResponse {

@JsonKey(name: 'variant_id') String get variantId; String get status; String? get message;
/// Create a copy of ApproveVariantResponse
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ApproveVariantResponseCopyWith<ApproveVariantResponse> get copyWith => _$ApproveVariantResponseCopyWithImpl<ApproveVariantResponse>(this as ApproveVariantResponse, _$identity);

  /// Serializes this ApproveVariantResponse to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ApproveVariantResponse&&(identical(other.variantId, variantId) || other.variantId == variantId)&&(identical(other.status, status) || other.status == status)&&(identical(other.message, message) || other.message == message));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,variantId,status,message);

@override
String toString() {
  return 'ApproveVariantResponse(variantId: $variantId, status: $status, message: $message)';
}


}

/// @nodoc
abstract mixin class $ApproveVariantResponseCopyWith<$Res>  {
  factory $ApproveVariantResponseCopyWith(ApproveVariantResponse value, $Res Function(ApproveVariantResponse) _then) = _$ApproveVariantResponseCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'variant_id') String variantId, String status, String? message
});




}
/// @nodoc
class _$ApproveVariantResponseCopyWithImpl<$Res>
    implements $ApproveVariantResponseCopyWith<$Res> {
  _$ApproveVariantResponseCopyWithImpl(this._self, this._then);

  final ApproveVariantResponse _self;
  final $Res Function(ApproveVariantResponse) _then;

/// Create a copy of ApproveVariantResponse
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? variantId = null,Object? status = null,Object? message = freezed,}) {
  return _then(_self.copyWith(
variantId: null == variantId ? _self.variantId : variantId // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,message: freezed == message ? _self.message : message // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [ApproveVariantResponse].
extension ApproveVariantResponsePatterns on ApproveVariantResponse {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ApproveVariantResponse value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ApproveVariantResponse() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ApproveVariantResponse value)  $default,){
final _that = this;
switch (_that) {
case _ApproveVariantResponse():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ApproveVariantResponse value)?  $default,){
final _that = this;
switch (_that) {
case _ApproveVariantResponse() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'variant_id')  String variantId,  String status,  String? message)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ApproveVariantResponse() when $default != null:
return $default(_that.variantId,_that.status,_that.message);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'variant_id')  String variantId,  String status,  String? message)  $default,) {final _that = this;
switch (_that) {
case _ApproveVariantResponse():
return $default(_that.variantId,_that.status,_that.message);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'variant_id')  String variantId,  String status,  String? message)?  $default,) {final _that = this;
switch (_that) {
case _ApproveVariantResponse() when $default != null:
return $default(_that.variantId,_that.status,_that.message);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ApproveVariantResponse implements ApproveVariantResponse {
  const _ApproveVariantResponse({@JsonKey(name: 'variant_id') required this.variantId, required this.status, this.message});
  factory _ApproveVariantResponse.fromJson(Map<String, dynamic> json) => _$ApproveVariantResponseFromJson(json);

@override@JsonKey(name: 'variant_id') final  String variantId;
@override final  String status;
@override final  String? message;

/// Create a copy of ApproveVariantResponse
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ApproveVariantResponseCopyWith<_ApproveVariantResponse> get copyWith => __$ApproveVariantResponseCopyWithImpl<_ApproveVariantResponse>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ApproveVariantResponseToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ApproveVariantResponse&&(identical(other.variantId, variantId) || other.variantId == variantId)&&(identical(other.status, status) || other.status == status)&&(identical(other.message, message) || other.message == message));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,variantId,status,message);

@override
String toString() {
  return 'ApproveVariantResponse(variantId: $variantId, status: $status, message: $message)';
}


}

/// @nodoc
abstract mixin class _$ApproveVariantResponseCopyWith<$Res> implements $ApproveVariantResponseCopyWith<$Res> {
  factory _$ApproveVariantResponseCopyWith(_ApproveVariantResponse value, $Res Function(_ApproveVariantResponse) _then) = __$ApproveVariantResponseCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'variant_id') String variantId, String status, String? message
});




}
/// @nodoc
class __$ApproveVariantResponseCopyWithImpl<$Res>
    implements _$ApproveVariantResponseCopyWith<$Res> {
  __$ApproveVariantResponseCopyWithImpl(this._self, this._then);

  final _ApproveVariantResponse _self;
  final $Res Function(_ApproveVariantResponse) _then;

/// Create a copy of ApproveVariantResponse
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? variantId = null,Object? status = null,Object? message = freezed,}) {
  return _then(_ApproveVariantResponse(
variantId: null == variantId ? _self.variantId : variantId // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,message: freezed == message ? _self.message : message // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$RejectVariantRequest {

@JsonKey(name: 'user_feedback') String? get userFeedback;
/// Create a copy of RejectVariantRequest
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RejectVariantRequestCopyWith<RejectVariantRequest> get copyWith => _$RejectVariantRequestCopyWithImpl<RejectVariantRequest>(this as RejectVariantRequest, _$identity);

  /// Serializes this RejectVariantRequest to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is RejectVariantRequest&&(identical(other.userFeedback, userFeedback) || other.userFeedback == userFeedback));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,userFeedback);

@override
String toString() {
  return 'RejectVariantRequest(userFeedback: $userFeedback)';
}


}

/// @nodoc
abstract mixin class $RejectVariantRequestCopyWith<$Res>  {
  factory $RejectVariantRequestCopyWith(RejectVariantRequest value, $Res Function(RejectVariantRequest) _then) = _$RejectVariantRequestCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'user_feedback') String? userFeedback
});




}
/// @nodoc
class _$RejectVariantRequestCopyWithImpl<$Res>
    implements $RejectVariantRequestCopyWith<$Res> {
  _$RejectVariantRequestCopyWithImpl(this._self, this._then);

  final RejectVariantRequest _self;
  final $Res Function(RejectVariantRequest) _then;

/// Create a copy of RejectVariantRequest
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? userFeedback = freezed,}) {
  return _then(_self.copyWith(
userFeedback: freezed == userFeedback ? _self.userFeedback : userFeedback // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [RejectVariantRequest].
extension RejectVariantRequestPatterns on RejectVariantRequest {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _RejectVariantRequest value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _RejectVariantRequest() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _RejectVariantRequest value)  $default,){
final _that = this;
switch (_that) {
case _RejectVariantRequest():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _RejectVariantRequest value)?  $default,){
final _that = this;
switch (_that) {
case _RejectVariantRequest() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'user_feedback')  String? userFeedback)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _RejectVariantRequest() when $default != null:
return $default(_that.userFeedback);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'user_feedback')  String? userFeedback)  $default,) {final _that = this;
switch (_that) {
case _RejectVariantRequest():
return $default(_that.userFeedback);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'user_feedback')  String? userFeedback)?  $default,) {final _that = this;
switch (_that) {
case _RejectVariantRequest() when $default != null:
return $default(_that.userFeedback);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _RejectVariantRequest implements RejectVariantRequest {
  const _RejectVariantRequest({@JsonKey(name: 'user_feedback') this.userFeedback});
  factory _RejectVariantRequest.fromJson(Map<String, dynamic> json) => _$RejectVariantRequestFromJson(json);

@override@JsonKey(name: 'user_feedback') final  String? userFeedback;

/// Create a copy of RejectVariantRequest
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RejectVariantRequestCopyWith<_RejectVariantRequest> get copyWith => __$RejectVariantRequestCopyWithImpl<_RejectVariantRequest>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$RejectVariantRequestToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _RejectVariantRequest&&(identical(other.userFeedback, userFeedback) || other.userFeedback == userFeedback));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,userFeedback);

@override
String toString() {
  return 'RejectVariantRequest(userFeedback: $userFeedback)';
}


}

/// @nodoc
abstract mixin class _$RejectVariantRequestCopyWith<$Res> implements $RejectVariantRequestCopyWith<$Res> {
  factory _$RejectVariantRequestCopyWith(_RejectVariantRequest value, $Res Function(_RejectVariantRequest) _then) = __$RejectVariantRequestCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'user_feedback') String? userFeedback
});




}
/// @nodoc
class __$RejectVariantRequestCopyWithImpl<$Res>
    implements _$RejectVariantRequestCopyWith<$Res> {
  __$RejectVariantRequestCopyWithImpl(this._self, this._then);

  final _RejectVariantRequest _self;
  final $Res Function(_RejectVariantRequest) _then;

/// Create a copy of RejectVariantRequest
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? userFeedback = freezed,}) {
  return _then(_RejectVariantRequest(
userFeedback: freezed == userFeedback ? _self.userFeedback : userFeedback // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on

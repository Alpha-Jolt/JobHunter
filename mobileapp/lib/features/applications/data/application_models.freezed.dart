// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'application_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ApplicationRecord {

@JsonKey(name: 'application_id') String get applicationId;@JsonKey(name: 'user_id') String get userId;@JsonKey(name: 'job_id') String get jobId;@JsonKey(name: 'resume_variant_id') String get resumeVariantId;/// Values: sent, replied, interview_scheduled, rejected, ghosted
 String get status;@JsonKey(name: 'sent_at') DateTime? get sentAt;@JsonKey(name: 'reply_count') int get replyCount;@JsonKey(name: 'thread_id') String? get threadId;@JsonKey(name: 'job_title') String? get jobTitle;@JsonKey(name: 'company_name') String? get companyName;
/// Create a copy of ApplicationRecord
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ApplicationRecordCopyWith<ApplicationRecord> get copyWith => _$ApplicationRecordCopyWithImpl<ApplicationRecord>(this as ApplicationRecord, _$identity);

  /// Serializes this ApplicationRecord to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ApplicationRecord&&(identical(other.applicationId, applicationId) || other.applicationId == applicationId)&&(identical(other.userId, userId) || other.userId == userId)&&(identical(other.jobId, jobId) || other.jobId == jobId)&&(identical(other.resumeVariantId, resumeVariantId) || other.resumeVariantId == resumeVariantId)&&(identical(other.status, status) || other.status == status)&&(identical(other.sentAt, sentAt) || other.sentAt == sentAt)&&(identical(other.replyCount, replyCount) || other.replyCount == replyCount)&&(identical(other.threadId, threadId) || other.threadId == threadId)&&(identical(other.jobTitle, jobTitle) || other.jobTitle == jobTitle)&&(identical(other.companyName, companyName) || other.companyName == companyName));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,applicationId,userId,jobId,resumeVariantId,status,sentAt,replyCount,threadId,jobTitle,companyName);

@override
String toString() {
  return 'ApplicationRecord(applicationId: $applicationId, userId: $userId, jobId: $jobId, resumeVariantId: $resumeVariantId, status: $status, sentAt: $sentAt, replyCount: $replyCount, threadId: $threadId, jobTitle: $jobTitle, companyName: $companyName)';
}


}

/// @nodoc
abstract mixin class $ApplicationRecordCopyWith<$Res>  {
  factory $ApplicationRecordCopyWith(ApplicationRecord value, $Res Function(ApplicationRecord) _then) = _$ApplicationRecordCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'application_id') String applicationId,@JsonKey(name: 'user_id') String userId,@JsonKey(name: 'job_id') String jobId,@JsonKey(name: 'resume_variant_id') String resumeVariantId, String status,@JsonKey(name: 'sent_at') DateTime? sentAt,@JsonKey(name: 'reply_count') int replyCount,@JsonKey(name: 'thread_id') String? threadId,@JsonKey(name: 'job_title') String? jobTitle,@JsonKey(name: 'company_name') String? companyName
});




}
/// @nodoc
class _$ApplicationRecordCopyWithImpl<$Res>
    implements $ApplicationRecordCopyWith<$Res> {
  _$ApplicationRecordCopyWithImpl(this._self, this._then);

  final ApplicationRecord _self;
  final $Res Function(ApplicationRecord) _then;

/// Create a copy of ApplicationRecord
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? applicationId = null,Object? userId = null,Object? jobId = null,Object? resumeVariantId = null,Object? status = null,Object? sentAt = freezed,Object? replyCount = null,Object? threadId = freezed,Object? jobTitle = freezed,Object? companyName = freezed,}) {
  return _then(_self.copyWith(
applicationId: null == applicationId ? _self.applicationId : applicationId // ignore: cast_nullable_to_non_nullable
as String,userId: null == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String,jobId: null == jobId ? _self.jobId : jobId // ignore: cast_nullable_to_non_nullable
as String,resumeVariantId: null == resumeVariantId ? _self.resumeVariantId : resumeVariantId // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,sentAt: freezed == sentAt ? _self.sentAt : sentAt // ignore: cast_nullable_to_non_nullable
as DateTime?,replyCount: null == replyCount ? _self.replyCount : replyCount // ignore: cast_nullable_to_non_nullable
as int,threadId: freezed == threadId ? _self.threadId : threadId // ignore: cast_nullable_to_non_nullable
as String?,jobTitle: freezed == jobTitle ? _self.jobTitle : jobTitle // ignore: cast_nullable_to_non_nullable
as String?,companyName: freezed == companyName ? _self.companyName : companyName // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [ApplicationRecord].
extension ApplicationRecordPatterns on ApplicationRecord {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ApplicationRecord value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ApplicationRecord() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ApplicationRecord value)  $default,){
final _that = this;
switch (_that) {
case _ApplicationRecord():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ApplicationRecord value)?  $default,){
final _that = this;
switch (_that) {
case _ApplicationRecord() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'application_id')  String applicationId, @JsonKey(name: 'user_id')  String userId, @JsonKey(name: 'job_id')  String jobId, @JsonKey(name: 'resume_variant_id')  String resumeVariantId,  String status, @JsonKey(name: 'sent_at')  DateTime? sentAt, @JsonKey(name: 'reply_count')  int replyCount, @JsonKey(name: 'thread_id')  String? threadId, @JsonKey(name: 'job_title')  String? jobTitle, @JsonKey(name: 'company_name')  String? companyName)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ApplicationRecord() when $default != null:
return $default(_that.applicationId,_that.userId,_that.jobId,_that.resumeVariantId,_that.status,_that.sentAt,_that.replyCount,_that.threadId,_that.jobTitle,_that.companyName);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'application_id')  String applicationId, @JsonKey(name: 'user_id')  String userId, @JsonKey(name: 'job_id')  String jobId, @JsonKey(name: 'resume_variant_id')  String resumeVariantId,  String status, @JsonKey(name: 'sent_at')  DateTime? sentAt, @JsonKey(name: 'reply_count')  int replyCount, @JsonKey(name: 'thread_id')  String? threadId, @JsonKey(name: 'job_title')  String? jobTitle, @JsonKey(name: 'company_name')  String? companyName)  $default,) {final _that = this;
switch (_that) {
case _ApplicationRecord():
return $default(_that.applicationId,_that.userId,_that.jobId,_that.resumeVariantId,_that.status,_that.sentAt,_that.replyCount,_that.threadId,_that.jobTitle,_that.companyName);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'application_id')  String applicationId, @JsonKey(name: 'user_id')  String userId, @JsonKey(name: 'job_id')  String jobId, @JsonKey(name: 'resume_variant_id')  String resumeVariantId,  String status, @JsonKey(name: 'sent_at')  DateTime? sentAt, @JsonKey(name: 'reply_count')  int replyCount, @JsonKey(name: 'thread_id')  String? threadId, @JsonKey(name: 'job_title')  String? jobTitle, @JsonKey(name: 'company_name')  String? companyName)?  $default,) {final _that = this;
switch (_that) {
case _ApplicationRecord() when $default != null:
return $default(_that.applicationId,_that.userId,_that.jobId,_that.resumeVariantId,_that.status,_that.sentAt,_that.replyCount,_that.threadId,_that.jobTitle,_that.companyName);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ApplicationRecord implements ApplicationRecord {
  const _ApplicationRecord({@JsonKey(name: 'application_id') required this.applicationId, @JsonKey(name: 'user_id') required this.userId, @JsonKey(name: 'job_id') required this.jobId, @JsonKey(name: 'resume_variant_id') required this.resumeVariantId, this.status = 'sent', @JsonKey(name: 'sent_at') this.sentAt, @JsonKey(name: 'reply_count') this.replyCount = 0, @JsonKey(name: 'thread_id') this.threadId, @JsonKey(name: 'job_title') this.jobTitle, @JsonKey(name: 'company_name') this.companyName});
  factory _ApplicationRecord.fromJson(Map<String, dynamic> json) => _$ApplicationRecordFromJson(json);

@override@JsonKey(name: 'application_id') final  String applicationId;
@override@JsonKey(name: 'user_id') final  String userId;
@override@JsonKey(name: 'job_id') final  String jobId;
@override@JsonKey(name: 'resume_variant_id') final  String resumeVariantId;
/// Values: sent, replied, interview_scheduled, rejected, ghosted
@override@JsonKey() final  String status;
@override@JsonKey(name: 'sent_at') final  DateTime? sentAt;
@override@JsonKey(name: 'reply_count') final  int replyCount;
@override@JsonKey(name: 'thread_id') final  String? threadId;
@override@JsonKey(name: 'job_title') final  String? jobTitle;
@override@JsonKey(name: 'company_name') final  String? companyName;

/// Create a copy of ApplicationRecord
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ApplicationRecordCopyWith<_ApplicationRecord> get copyWith => __$ApplicationRecordCopyWithImpl<_ApplicationRecord>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ApplicationRecordToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ApplicationRecord&&(identical(other.applicationId, applicationId) || other.applicationId == applicationId)&&(identical(other.userId, userId) || other.userId == userId)&&(identical(other.jobId, jobId) || other.jobId == jobId)&&(identical(other.resumeVariantId, resumeVariantId) || other.resumeVariantId == resumeVariantId)&&(identical(other.status, status) || other.status == status)&&(identical(other.sentAt, sentAt) || other.sentAt == sentAt)&&(identical(other.replyCount, replyCount) || other.replyCount == replyCount)&&(identical(other.threadId, threadId) || other.threadId == threadId)&&(identical(other.jobTitle, jobTitle) || other.jobTitle == jobTitle)&&(identical(other.companyName, companyName) || other.companyName == companyName));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,applicationId,userId,jobId,resumeVariantId,status,sentAt,replyCount,threadId,jobTitle,companyName);

@override
String toString() {
  return 'ApplicationRecord(applicationId: $applicationId, userId: $userId, jobId: $jobId, resumeVariantId: $resumeVariantId, status: $status, sentAt: $sentAt, replyCount: $replyCount, threadId: $threadId, jobTitle: $jobTitle, companyName: $companyName)';
}


}

/// @nodoc
abstract mixin class _$ApplicationRecordCopyWith<$Res> implements $ApplicationRecordCopyWith<$Res> {
  factory _$ApplicationRecordCopyWith(_ApplicationRecord value, $Res Function(_ApplicationRecord) _then) = __$ApplicationRecordCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'application_id') String applicationId,@JsonKey(name: 'user_id') String userId,@JsonKey(name: 'job_id') String jobId,@JsonKey(name: 'resume_variant_id') String resumeVariantId, String status,@JsonKey(name: 'sent_at') DateTime? sentAt,@JsonKey(name: 'reply_count') int replyCount,@JsonKey(name: 'thread_id') String? threadId,@JsonKey(name: 'job_title') String? jobTitle,@JsonKey(name: 'company_name') String? companyName
});




}
/// @nodoc
class __$ApplicationRecordCopyWithImpl<$Res>
    implements _$ApplicationRecordCopyWith<$Res> {
  __$ApplicationRecordCopyWithImpl(this._self, this._then);

  final _ApplicationRecord _self;
  final $Res Function(_ApplicationRecord) _then;

/// Create a copy of ApplicationRecord
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? applicationId = null,Object? userId = null,Object? jobId = null,Object? resumeVariantId = null,Object? status = null,Object? sentAt = freezed,Object? replyCount = null,Object? threadId = freezed,Object? jobTitle = freezed,Object? companyName = freezed,}) {
  return _then(_ApplicationRecord(
applicationId: null == applicationId ? _self.applicationId : applicationId // ignore: cast_nullable_to_non_nullable
as String,userId: null == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String,jobId: null == jobId ? _self.jobId : jobId // ignore: cast_nullable_to_non_nullable
as String,resumeVariantId: null == resumeVariantId ? _self.resumeVariantId : resumeVariantId // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,sentAt: freezed == sentAt ? _self.sentAt : sentAt // ignore: cast_nullable_to_non_nullable
as DateTime?,replyCount: null == replyCount ? _self.replyCount : replyCount // ignore: cast_nullable_to_non_nullable
as int,threadId: freezed == threadId ? _self.threadId : threadId // ignore: cast_nullable_to_non_nullable
as String?,jobTitle: freezed == jobTitle ? _self.jobTitle : jobTitle // ignore: cast_nullable_to_non_nullable
as String?,companyName: freezed == companyName ? _self.companyName : companyName // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$SentTodayResponse {

 int get count; List<ApplicationRecord> get applications;
/// Create a copy of SentTodayResponse
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SentTodayResponseCopyWith<SentTodayResponse> get copyWith => _$SentTodayResponseCopyWithImpl<SentTodayResponse>(this as SentTodayResponse, _$identity);

  /// Serializes this SentTodayResponse to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SentTodayResponse&&(identical(other.count, count) || other.count == count)&&const DeepCollectionEquality().equals(other.applications, applications));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,count,const DeepCollectionEquality().hash(applications));

@override
String toString() {
  return 'SentTodayResponse(count: $count, applications: $applications)';
}


}

/// @nodoc
abstract mixin class $SentTodayResponseCopyWith<$Res>  {
  factory $SentTodayResponseCopyWith(SentTodayResponse value, $Res Function(SentTodayResponse) _then) = _$SentTodayResponseCopyWithImpl;
@useResult
$Res call({
 int count, List<ApplicationRecord> applications
});




}
/// @nodoc
class _$SentTodayResponseCopyWithImpl<$Res>
    implements $SentTodayResponseCopyWith<$Res> {
  _$SentTodayResponseCopyWithImpl(this._self, this._then);

  final SentTodayResponse _self;
  final $Res Function(SentTodayResponse) _then;

/// Create a copy of SentTodayResponse
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? count = null,Object? applications = null,}) {
  return _then(_self.copyWith(
count: null == count ? _self.count : count // ignore: cast_nullable_to_non_nullable
as int,applications: null == applications ? _self.applications : applications // ignore: cast_nullable_to_non_nullable
as List<ApplicationRecord>,
  ));
}

}


/// Adds pattern-matching-related methods to [SentTodayResponse].
extension SentTodayResponsePatterns on SentTodayResponse {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _SentTodayResponse value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _SentTodayResponse() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _SentTodayResponse value)  $default,){
final _that = this;
switch (_that) {
case _SentTodayResponse():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _SentTodayResponse value)?  $default,){
final _that = this;
switch (_that) {
case _SentTodayResponse() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int count,  List<ApplicationRecord> applications)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _SentTodayResponse() when $default != null:
return $default(_that.count,_that.applications);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int count,  List<ApplicationRecord> applications)  $default,) {final _that = this;
switch (_that) {
case _SentTodayResponse():
return $default(_that.count,_that.applications);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int count,  List<ApplicationRecord> applications)?  $default,) {final _that = this;
switch (_that) {
case _SentTodayResponse() when $default != null:
return $default(_that.count,_that.applications);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _SentTodayResponse implements SentTodayResponse {
  const _SentTodayResponse({required this.count, required final  List<ApplicationRecord> applications}): _applications = applications;
  factory _SentTodayResponse.fromJson(Map<String, dynamic> json) => _$SentTodayResponseFromJson(json);

@override final  int count;
 final  List<ApplicationRecord> _applications;
@override List<ApplicationRecord> get applications {
  if (_applications is EqualUnmodifiableListView) return _applications;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_applications);
}


/// Create a copy of SentTodayResponse
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$SentTodayResponseCopyWith<_SentTodayResponse> get copyWith => __$SentTodayResponseCopyWithImpl<_SentTodayResponse>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SentTodayResponseToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _SentTodayResponse&&(identical(other.count, count) || other.count == count)&&const DeepCollectionEquality().equals(other._applications, _applications));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,count,const DeepCollectionEquality().hash(_applications));

@override
String toString() {
  return 'SentTodayResponse(count: $count, applications: $applications)';
}


}

/// @nodoc
abstract mixin class _$SentTodayResponseCopyWith<$Res> implements $SentTodayResponseCopyWith<$Res> {
  factory _$SentTodayResponseCopyWith(_SentTodayResponse value, $Res Function(_SentTodayResponse) _then) = __$SentTodayResponseCopyWithImpl;
@override @useResult
$Res call({
 int count, List<ApplicationRecord> applications
});




}
/// @nodoc
class __$SentTodayResponseCopyWithImpl<$Res>
    implements _$SentTodayResponseCopyWith<$Res> {
  __$SentTodayResponseCopyWithImpl(this._self, this._then);

  final _SentTodayResponse _self;
  final $Res Function(_SentTodayResponse) _then;

/// Create a copy of SentTodayResponse
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? count = null,Object? applications = null,}) {
  return _then(_SentTodayResponse(
count: null == count ? _self.count : count // ignore: cast_nullable_to_non_nullable
as int,applications: null == applications ? _self._applications : applications // ignore: cast_nullable_to_non_nullable
as List<ApplicationRecord>,
  ));
}


}


/// @nodoc
mixin _$SendApplicationRequest {

@JsonKey(name: 'user_id') String get userId;@JsonKey(name: 'job_id') String get jobId;@JsonKey(name: 'variant_id') String get variantId;@JsonKey(name: 'user_name') String get userName;@JsonKey(name: 'user_email') String get userEmail;@JsonKey(name: 'user_phone') String? get userPhone;@JsonKey(name: 'user_summary') String? get userSummary;
/// Create a copy of SendApplicationRequest
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SendApplicationRequestCopyWith<SendApplicationRequest> get copyWith => _$SendApplicationRequestCopyWithImpl<SendApplicationRequest>(this as SendApplicationRequest, _$identity);

  /// Serializes this SendApplicationRequest to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SendApplicationRequest&&(identical(other.userId, userId) || other.userId == userId)&&(identical(other.jobId, jobId) || other.jobId == jobId)&&(identical(other.variantId, variantId) || other.variantId == variantId)&&(identical(other.userName, userName) || other.userName == userName)&&(identical(other.userEmail, userEmail) || other.userEmail == userEmail)&&(identical(other.userPhone, userPhone) || other.userPhone == userPhone)&&(identical(other.userSummary, userSummary) || other.userSummary == userSummary));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,userId,jobId,variantId,userName,userEmail,userPhone,userSummary);

@override
String toString() {
  return 'SendApplicationRequest(userId: $userId, jobId: $jobId, variantId: $variantId, userName: $userName, userEmail: $userEmail, userPhone: $userPhone, userSummary: $userSummary)';
}


}

/// @nodoc
abstract mixin class $SendApplicationRequestCopyWith<$Res>  {
  factory $SendApplicationRequestCopyWith(SendApplicationRequest value, $Res Function(SendApplicationRequest) _then) = _$SendApplicationRequestCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'user_id') String userId,@JsonKey(name: 'job_id') String jobId,@JsonKey(name: 'variant_id') String variantId,@JsonKey(name: 'user_name') String userName,@JsonKey(name: 'user_email') String userEmail,@JsonKey(name: 'user_phone') String? userPhone,@JsonKey(name: 'user_summary') String? userSummary
});




}
/// @nodoc
class _$SendApplicationRequestCopyWithImpl<$Res>
    implements $SendApplicationRequestCopyWith<$Res> {
  _$SendApplicationRequestCopyWithImpl(this._self, this._then);

  final SendApplicationRequest _self;
  final $Res Function(SendApplicationRequest) _then;

/// Create a copy of SendApplicationRequest
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? userId = null,Object? jobId = null,Object? variantId = null,Object? userName = null,Object? userEmail = null,Object? userPhone = freezed,Object? userSummary = freezed,}) {
  return _then(_self.copyWith(
userId: null == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String,jobId: null == jobId ? _self.jobId : jobId // ignore: cast_nullable_to_non_nullable
as String,variantId: null == variantId ? _self.variantId : variantId // ignore: cast_nullable_to_non_nullable
as String,userName: null == userName ? _self.userName : userName // ignore: cast_nullable_to_non_nullable
as String,userEmail: null == userEmail ? _self.userEmail : userEmail // ignore: cast_nullable_to_non_nullable
as String,userPhone: freezed == userPhone ? _self.userPhone : userPhone // ignore: cast_nullable_to_non_nullable
as String?,userSummary: freezed == userSummary ? _self.userSummary : userSummary // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [SendApplicationRequest].
extension SendApplicationRequestPatterns on SendApplicationRequest {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _SendApplicationRequest value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _SendApplicationRequest() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _SendApplicationRequest value)  $default,){
final _that = this;
switch (_that) {
case _SendApplicationRequest():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _SendApplicationRequest value)?  $default,){
final _that = this;
switch (_that) {
case _SendApplicationRequest() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'user_id')  String userId, @JsonKey(name: 'job_id')  String jobId, @JsonKey(name: 'variant_id')  String variantId, @JsonKey(name: 'user_name')  String userName, @JsonKey(name: 'user_email')  String userEmail, @JsonKey(name: 'user_phone')  String? userPhone, @JsonKey(name: 'user_summary')  String? userSummary)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _SendApplicationRequest() when $default != null:
return $default(_that.userId,_that.jobId,_that.variantId,_that.userName,_that.userEmail,_that.userPhone,_that.userSummary);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'user_id')  String userId, @JsonKey(name: 'job_id')  String jobId, @JsonKey(name: 'variant_id')  String variantId, @JsonKey(name: 'user_name')  String userName, @JsonKey(name: 'user_email')  String userEmail, @JsonKey(name: 'user_phone')  String? userPhone, @JsonKey(name: 'user_summary')  String? userSummary)  $default,) {final _that = this;
switch (_that) {
case _SendApplicationRequest():
return $default(_that.userId,_that.jobId,_that.variantId,_that.userName,_that.userEmail,_that.userPhone,_that.userSummary);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'user_id')  String userId, @JsonKey(name: 'job_id')  String jobId, @JsonKey(name: 'variant_id')  String variantId, @JsonKey(name: 'user_name')  String userName, @JsonKey(name: 'user_email')  String userEmail, @JsonKey(name: 'user_phone')  String? userPhone, @JsonKey(name: 'user_summary')  String? userSummary)?  $default,) {final _that = this;
switch (_that) {
case _SendApplicationRequest() when $default != null:
return $default(_that.userId,_that.jobId,_that.variantId,_that.userName,_that.userEmail,_that.userPhone,_that.userSummary);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _SendApplicationRequest implements SendApplicationRequest {
  const _SendApplicationRequest({@JsonKey(name: 'user_id') required this.userId, @JsonKey(name: 'job_id') required this.jobId, @JsonKey(name: 'variant_id') required this.variantId, @JsonKey(name: 'user_name') required this.userName, @JsonKey(name: 'user_email') required this.userEmail, @JsonKey(name: 'user_phone') this.userPhone, @JsonKey(name: 'user_summary') this.userSummary});
  factory _SendApplicationRequest.fromJson(Map<String, dynamic> json) => _$SendApplicationRequestFromJson(json);

@override@JsonKey(name: 'user_id') final  String userId;
@override@JsonKey(name: 'job_id') final  String jobId;
@override@JsonKey(name: 'variant_id') final  String variantId;
@override@JsonKey(name: 'user_name') final  String userName;
@override@JsonKey(name: 'user_email') final  String userEmail;
@override@JsonKey(name: 'user_phone') final  String? userPhone;
@override@JsonKey(name: 'user_summary') final  String? userSummary;

/// Create a copy of SendApplicationRequest
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$SendApplicationRequestCopyWith<_SendApplicationRequest> get copyWith => __$SendApplicationRequestCopyWithImpl<_SendApplicationRequest>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SendApplicationRequestToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _SendApplicationRequest&&(identical(other.userId, userId) || other.userId == userId)&&(identical(other.jobId, jobId) || other.jobId == jobId)&&(identical(other.variantId, variantId) || other.variantId == variantId)&&(identical(other.userName, userName) || other.userName == userName)&&(identical(other.userEmail, userEmail) || other.userEmail == userEmail)&&(identical(other.userPhone, userPhone) || other.userPhone == userPhone)&&(identical(other.userSummary, userSummary) || other.userSummary == userSummary));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,userId,jobId,variantId,userName,userEmail,userPhone,userSummary);

@override
String toString() {
  return 'SendApplicationRequest(userId: $userId, jobId: $jobId, variantId: $variantId, userName: $userName, userEmail: $userEmail, userPhone: $userPhone, userSummary: $userSummary)';
}


}

/// @nodoc
abstract mixin class _$SendApplicationRequestCopyWith<$Res> implements $SendApplicationRequestCopyWith<$Res> {
  factory _$SendApplicationRequestCopyWith(_SendApplicationRequest value, $Res Function(_SendApplicationRequest) _then) = __$SendApplicationRequestCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'user_id') String userId,@JsonKey(name: 'job_id') String jobId,@JsonKey(name: 'variant_id') String variantId,@JsonKey(name: 'user_name') String userName,@JsonKey(name: 'user_email') String userEmail,@JsonKey(name: 'user_phone') String? userPhone,@JsonKey(name: 'user_summary') String? userSummary
});




}
/// @nodoc
class __$SendApplicationRequestCopyWithImpl<$Res>
    implements _$SendApplicationRequestCopyWith<$Res> {
  __$SendApplicationRequestCopyWithImpl(this._self, this._then);

  final _SendApplicationRequest _self;
  final $Res Function(_SendApplicationRequest) _then;

/// Create a copy of SendApplicationRequest
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? userId = null,Object? jobId = null,Object? variantId = null,Object? userName = null,Object? userEmail = null,Object? userPhone = freezed,Object? userSummary = freezed,}) {
  return _then(_SendApplicationRequest(
userId: null == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String,jobId: null == jobId ? _self.jobId : jobId // ignore: cast_nullable_to_non_nullable
as String,variantId: null == variantId ? _self.variantId : variantId // ignore: cast_nullable_to_non_nullable
as String,userName: null == userName ? _self.userName : userName // ignore: cast_nullable_to_non_nullable
as String,userEmail: null == userEmail ? _self.userEmail : userEmail // ignore: cast_nullable_to_non_nullable
as String,userPhone: freezed == userPhone ? _self.userPhone : userPhone // ignore: cast_nullable_to_non_nullable
as String?,userSummary: freezed == userSummary ? _self.userSummary : userSummary // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$ApplicationStatus {

 String get status;@JsonKey(name: 'sent_at') DateTime? get sentAt;@JsonKey(name: 'reply_count') int get replyCount;
/// Create a copy of ApplicationStatus
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ApplicationStatusCopyWith<ApplicationStatus> get copyWith => _$ApplicationStatusCopyWithImpl<ApplicationStatus>(this as ApplicationStatus, _$identity);

  /// Serializes this ApplicationStatus to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ApplicationStatus&&(identical(other.status, status) || other.status == status)&&(identical(other.sentAt, sentAt) || other.sentAt == sentAt)&&(identical(other.replyCount, replyCount) || other.replyCount == replyCount));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,status,sentAt,replyCount);

@override
String toString() {
  return 'ApplicationStatus(status: $status, sentAt: $sentAt, replyCount: $replyCount)';
}


}

/// @nodoc
abstract mixin class $ApplicationStatusCopyWith<$Res>  {
  factory $ApplicationStatusCopyWith(ApplicationStatus value, $Res Function(ApplicationStatus) _then) = _$ApplicationStatusCopyWithImpl;
@useResult
$Res call({
 String status,@JsonKey(name: 'sent_at') DateTime? sentAt,@JsonKey(name: 'reply_count') int replyCount
});




}
/// @nodoc
class _$ApplicationStatusCopyWithImpl<$Res>
    implements $ApplicationStatusCopyWith<$Res> {
  _$ApplicationStatusCopyWithImpl(this._self, this._then);

  final ApplicationStatus _self;
  final $Res Function(ApplicationStatus) _then;

/// Create a copy of ApplicationStatus
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? status = null,Object? sentAt = freezed,Object? replyCount = null,}) {
  return _then(_self.copyWith(
status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,sentAt: freezed == sentAt ? _self.sentAt : sentAt // ignore: cast_nullable_to_non_nullable
as DateTime?,replyCount: null == replyCount ? _self.replyCount : replyCount // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [ApplicationStatus].
extension ApplicationStatusPatterns on ApplicationStatus {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ApplicationStatus value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ApplicationStatus() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ApplicationStatus value)  $default,){
final _that = this;
switch (_that) {
case _ApplicationStatus():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ApplicationStatus value)?  $default,){
final _that = this;
switch (_that) {
case _ApplicationStatus() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String status, @JsonKey(name: 'sent_at')  DateTime? sentAt, @JsonKey(name: 'reply_count')  int replyCount)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ApplicationStatus() when $default != null:
return $default(_that.status,_that.sentAt,_that.replyCount);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String status, @JsonKey(name: 'sent_at')  DateTime? sentAt, @JsonKey(name: 'reply_count')  int replyCount)  $default,) {final _that = this;
switch (_that) {
case _ApplicationStatus():
return $default(_that.status,_that.sentAt,_that.replyCount);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String status, @JsonKey(name: 'sent_at')  DateTime? sentAt, @JsonKey(name: 'reply_count')  int replyCount)?  $default,) {final _that = this;
switch (_that) {
case _ApplicationStatus() when $default != null:
return $default(_that.status,_that.sentAt,_that.replyCount);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ApplicationStatus implements ApplicationStatus {
  const _ApplicationStatus({required this.status, @JsonKey(name: 'sent_at') this.sentAt, @JsonKey(name: 'reply_count') this.replyCount = 0});
  factory _ApplicationStatus.fromJson(Map<String, dynamic> json) => _$ApplicationStatusFromJson(json);

@override final  String status;
@override@JsonKey(name: 'sent_at') final  DateTime? sentAt;
@override@JsonKey(name: 'reply_count') final  int replyCount;

/// Create a copy of ApplicationStatus
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ApplicationStatusCopyWith<_ApplicationStatus> get copyWith => __$ApplicationStatusCopyWithImpl<_ApplicationStatus>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ApplicationStatusToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ApplicationStatus&&(identical(other.status, status) || other.status == status)&&(identical(other.sentAt, sentAt) || other.sentAt == sentAt)&&(identical(other.replyCount, replyCount) || other.replyCount == replyCount));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,status,sentAt,replyCount);

@override
String toString() {
  return 'ApplicationStatus(status: $status, sentAt: $sentAt, replyCount: $replyCount)';
}


}

/// @nodoc
abstract mixin class _$ApplicationStatusCopyWith<$Res> implements $ApplicationStatusCopyWith<$Res> {
  factory _$ApplicationStatusCopyWith(_ApplicationStatus value, $Res Function(_ApplicationStatus) _then) = __$ApplicationStatusCopyWithImpl;
@override @useResult
$Res call({
 String status,@JsonKey(name: 'sent_at') DateTime? sentAt,@JsonKey(name: 'reply_count') int replyCount
});




}
/// @nodoc
class __$ApplicationStatusCopyWithImpl<$Res>
    implements _$ApplicationStatusCopyWith<$Res> {
  __$ApplicationStatusCopyWithImpl(this._self, this._then);

  final _ApplicationStatus _self;
  final $Res Function(_ApplicationStatus) _then;

/// Create a copy of ApplicationStatus
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? status = null,Object? sentAt = freezed,Object? replyCount = null,}) {
  return _then(_ApplicationStatus(
status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,sentAt: freezed == sentAt ? _self.sentAt : sentAt // ignore: cast_nullable_to_non_nullable
as DateTime?,replyCount: null == replyCount ? _self.replyCount : replyCount // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}

// dart format on

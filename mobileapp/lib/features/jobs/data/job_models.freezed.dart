// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'job_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$JobRecord {

@JsonKey(name: 'job_id') String get jobId; String get title;@JsonKey(name: 'company_name') String get companyName; String get location;@JsonKey(name: 'remote_type') String? get remoteType;@JsonKey(name: 'salary_min') int? get salaryMin;@JsonKey(name: 'salary_max') int? get salaryMax;@JsonKey(name: 'experience_min') int? get experienceMin;@JsonKey(name: 'experience_max') int? get experienceMax; String? get description;@JsonKey(name: 'skills_required') List<String> get skillsRequired;@JsonKey(name: 'job_type') String? get jobType;@JsonKey(name: 'apply_email') String? get applyEmail;@JsonKey(name: 'email_trust') String get emailTrust;@JsonKey(name: 'apply_url') String? get applyUrl; String get status; String? get source;
/// Create a copy of JobRecord
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$JobRecordCopyWith<JobRecord> get copyWith => _$JobRecordCopyWithImpl<JobRecord>(this as JobRecord, _$identity);

  /// Serializes this JobRecord to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is JobRecord&&(identical(other.jobId, jobId) || other.jobId == jobId)&&(identical(other.title, title) || other.title == title)&&(identical(other.companyName, companyName) || other.companyName == companyName)&&(identical(other.location, location) || other.location == location)&&(identical(other.remoteType, remoteType) || other.remoteType == remoteType)&&(identical(other.salaryMin, salaryMin) || other.salaryMin == salaryMin)&&(identical(other.salaryMax, salaryMax) || other.salaryMax == salaryMax)&&(identical(other.experienceMin, experienceMin) || other.experienceMin == experienceMin)&&(identical(other.experienceMax, experienceMax) || other.experienceMax == experienceMax)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other.skillsRequired, skillsRequired)&&(identical(other.jobType, jobType) || other.jobType == jobType)&&(identical(other.applyEmail, applyEmail) || other.applyEmail == applyEmail)&&(identical(other.emailTrust, emailTrust) || other.emailTrust == emailTrust)&&(identical(other.applyUrl, applyUrl) || other.applyUrl == applyUrl)&&(identical(other.status, status) || other.status == status)&&(identical(other.source, source) || other.source == source));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,jobId,title,companyName,location,remoteType,salaryMin,salaryMax,experienceMin,experienceMax,description,const DeepCollectionEquality().hash(skillsRequired),jobType,applyEmail,emailTrust,applyUrl,status,source);

@override
String toString() {
  return 'JobRecord(jobId: $jobId, title: $title, companyName: $companyName, location: $location, remoteType: $remoteType, salaryMin: $salaryMin, salaryMax: $salaryMax, experienceMin: $experienceMin, experienceMax: $experienceMax, description: $description, skillsRequired: $skillsRequired, jobType: $jobType, applyEmail: $applyEmail, emailTrust: $emailTrust, applyUrl: $applyUrl, status: $status, source: $source)';
}


}

/// @nodoc
abstract mixin class $JobRecordCopyWith<$Res>  {
  factory $JobRecordCopyWith(JobRecord value, $Res Function(JobRecord) _then) = _$JobRecordCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'job_id') String jobId, String title,@JsonKey(name: 'company_name') String companyName, String location,@JsonKey(name: 'remote_type') String? remoteType,@JsonKey(name: 'salary_min') int? salaryMin,@JsonKey(name: 'salary_max') int? salaryMax,@JsonKey(name: 'experience_min') int? experienceMin,@JsonKey(name: 'experience_max') int? experienceMax, String? description,@JsonKey(name: 'skills_required') List<String> skillsRequired,@JsonKey(name: 'job_type') String? jobType,@JsonKey(name: 'apply_email') String? applyEmail,@JsonKey(name: 'email_trust') String emailTrust,@JsonKey(name: 'apply_url') String? applyUrl, String status, String? source
});




}
/// @nodoc
class _$JobRecordCopyWithImpl<$Res>
    implements $JobRecordCopyWith<$Res> {
  _$JobRecordCopyWithImpl(this._self, this._then);

  final JobRecord _self;
  final $Res Function(JobRecord) _then;

/// Create a copy of JobRecord
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? jobId = null,Object? title = null,Object? companyName = null,Object? location = null,Object? remoteType = freezed,Object? salaryMin = freezed,Object? salaryMax = freezed,Object? experienceMin = freezed,Object? experienceMax = freezed,Object? description = freezed,Object? skillsRequired = null,Object? jobType = freezed,Object? applyEmail = freezed,Object? emailTrust = null,Object? applyUrl = freezed,Object? status = null,Object? source = freezed,}) {
  return _then(_self.copyWith(
jobId: null == jobId ? _self.jobId : jobId // ignore: cast_nullable_to_non_nullable
as String,title: null == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as String,companyName: null == companyName ? _self.companyName : companyName // ignore: cast_nullable_to_non_nullable
as String,location: null == location ? _self.location : location // ignore: cast_nullable_to_non_nullable
as String,remoteType: freezed == remoteType ? _self.remoteType : remoteType // ignore: cast_nullable_to_non_nullable
as String?,salaryMin: freezed == salaryMin ? _self.salaryMin : salaryMin // ignore: cast_nullable_to_non_nullable
as int?,salaryMax: freezed == salaryMax ? _self.salaryMax : salaryMax // ignore: cast_nullable_to_non_nullable
as int?,experienceMin: freezed == experienceMin ? _self.experienceMin : experienceMin // ignore: cast_nullable_to_non_nullable
as int?,experienceMax: freezed == experienceMax ? _self.experienceMax : experienceMax // ignore: cast_nullable_to_non_nullable
as int?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,skillsRequired: null == skillsRequired ? _self.skillsRequired : skillsRequired // ignore: cast_nullable_to_non_nullable
as List<String>,jobType: freezed == jobType ? _self.jobType : jobType // ignore: cast_nullable_to_non_nullable
as String?,applyEmail: freezed == applyEmail ? _self.applyEmail : applyEmail // ignore: cast_nullable_to_non_nullable
as String?,emailTrust: null == emailTrust ? _self.emailTrust : emailTrust // ignore: cast_nullable_to_non_nullable
as String,applyUrl: freezed == applyUrl ? _self.applyUrl : applyUrl // ignore: cast_nullable_to_non_nullable
as String?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,source: freezed == source ? _self.source : source // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [JobRecord].
extension JobRecordPatterns on JobRecord {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _JobRecord value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _JobRecord() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _JobRecord value)  $default,){
final _that = this;
switch (_that) {
case _JobRecord():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _JobRecord value)?  $default,){
final _that = this;
switch (_that) {
case _JobRecord() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'job_id')  String jobId,  String title, @JsonKey(name: 'company_name')  String companyName,  String location, @JsonKey(name: 'remote_type')  String? remoteType, @JsonKey(name: 'salary_min')  int? salaryMin, @JsonKey(name: 'salary_max')  int? salaryMax, @JsonKey(name: 'experience_min')  int? experienceMin, @JsonKey(name: 'experience_max')  int? experienceMax,  String? description, @JsonKey(name: 'skills_required')  List<String> skillsRequired, @JsonKey(name: 'job_type')  String? jobType, @JsonKey(name: 'apply_email')  String? applyEmail, @JsonKey(name: 'email_trust')  String emailTrust, @JsonKey(name: 'apply_url')  String? applyUrl,  String status,  String? source)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _JobRecord() when $default != null:
return $default(_that.jobId,_that.title,_that.companyName,_that.location,_that.remoteType,_that.salaryMin,_that.salaryMax,_that.experienceMin,_that.experienceMax,_that.description,_that.skillsRequired,_that.jobType,_that.applyEmail,_that.emailTrust,_that.applyUrl,_that.status,_that.source);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'job_id')  String jobId,  String title, @JsonKey(name: 'company_name')  String companyName,  String location, @JsonKey(name: 'remote_type')  String? remoteType, @JsonKey(name: 'salary_min')  int? salaryMin, @JsonKey(name: 'salary_max')  int? salaryMax, @JsonKey(name: 'experience_min')  int? experienceMin, @JsonKey(name: 'experience_max')  int? experienceMax,  String? description, @JsonKey(name: 'skills_required')  List<String> skillsRequired, @JsonKey(name: 'job_type')  String? jobType, @JsonKey(name: 'apply_email')  String? applyEmail, @JsonKey(name: 'email_trust')  String emailTrust, @JsonKey(name: 'apply_url')  String? applyUrl,  String status,  String? source)  $default,) {final _that = this;
switch (_that) {
case _JobRecord():
return $default(_that.jobId,_that.title,_that.companyName,_that.location,_that.remoteType,_that.salaryMin,_that.salaryMax,_that.experienceMin,_that.experienceMax,_that.description,_that.skillsRequired,_that.jobType,_that.applyEmail,_that.emailTrust,_that.applyUrl,_that.status,_that.source);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'job_id')  String jobId,  String title, @JsonKey(name: 'company_name')  String companyName,  String location, @JsonKey(name: 'remote_type')  String? remoteType, @JsonKey(name: 'salary_min')  int? salaryMin, @JsonKey(name: 'salary_max')  int? salaryMax, @JsonKey(name: 'experience_min')  int? experienceMin, @JsonKey(name: 'experience_max')  int? experienceMax,  String? description, @JsonKey(name: 'skills_required')  List<String> skillsRequired, @JsonKey(name: 'job_type')  String? jobType, @JsonKey(name: 'apply_email')  String? applyEmail, @JsonKey(name: 'email_trust')  String emailTrust, @JsonKey(name: 'apply_url')  String? applyUrl,  String status,  String? source)?  $default,) {final _that = this;
switch (_that) {
case _JobRecord() when $default != null:
return $default(_that.jobId,_that.title,_that.companyName,_that.location,_that.remoteType,_that.salaryMin,_that.salaryMax,_that.experienceMin,_that.experienceMax,_that.description,_that.skillsRequired,_that.jobType,_that.applyEmail,_that.emailTrust,_that.applyUrl,_that.status,_that.source);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _JobRecord implements JobRecord {
  const _JobRecord({@JsonKey(name: 'job_id') required this.jobId, required this.title, @JsonKey(name: 'company_name') required this.companyName, required this.location, @JsonKey(name: 'remote_type') this.remoteType, @JsonKey(name: 'salary_min') this.salaryMin, @JsonKey(name: 'salary_max') this.salaryMax, @JsonKey(name: 'experience_min') this.experienceMin, @JsonKey(name: 'experience_max') this.experienceMax, this.description, @JsonKey(name: 'skills_required') final  List<String> skillsRequired = const [], @JsonKey(name: 'job_type') this.jobType, @JsonKey(name: 'apply_email') this.applyEmail, @JsonKey(name: 'email_trust') this.emailTrust = 'unknown', @JsonKey(name: 'apply_url') this.applyUrl, this.status = 'raw', this.source}): _skillsRequired = skillsRequired;
  factory _JobRecord.fromJson(Map<String, dynamic> json) => _$JobRecordFromJson(json);

@override@JsonKey(name: 'job_id') final  String jobId;
@override final  String title;
@override@JsonKey(name: 'company_name') final  String companyName;
@override final  String location;
@override@JsonKey(name: 'remote_type') final  String? remoteType;
@override@JsonKey(name: 'salary_min') final  int? salaryMin;
@override@JsonKey(name: 'salary_max') final  int? salaryMax;
@override@JsonKey(name: 'experience_min') final  int? experienceMin;
@override@JsonKey(name: 'experience_max') final  int? experienceMax;
@override final  String? description;
 final  List<String> _skillsRequired;
@override@JsonKey(name: 'skills_required') List<String> get skillsRequired {
  if (_skillsRequired is EqualUnmodifiableListView) return _skillsRequired;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_skillsRequired);
}

@override@JsonKey(name: 'job_type') final  String? jobType;
@override@JsonKey(name: 'apply_email') final  String? applyEmail;
@override@JsonKey(name: 'email_trust') final  String emailTrust;
@override@JsonKey(name: 'apply_url') final  String? applyUrl;
@override@JsonKey() final  String status;
@override final  String? source;

/// Create a copy of JobRecord
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$JobRecordCopyWith<_JobRecord> get copyWith => __$JobRecordCopyWithImpl<_JobRecord>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$JobRecordToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _JobRecord&&(identical(other.jobId, jobId) || other.jobId == jobId)&&(identical(other.title, title) || other.title == title)&&(identical(other.companyName, companyName) || other.companyName == companyName)&&(identical(other.location, location) || other.location == location)&&(identical(other.remoteType, remoteType) || other.remoteType == remoteType)&&(identical(other.salaryMin, salaryMin) || other.salaryMin == salaryMin)&&(identical(other.salaryMax, salaryMax) || other.salaryMax == salaryMax)&&(identical(other.experienceMin, experienceMin) || other.experienceMin == experienceMin)&&(identical(other.experienceMax, experienceMax) || other.experienceMax == experienceMax)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other._skillsRequired, _skillsRequired)&&(identical(other.jobType, jobType) || other.jobType == jobType)&&(identical(other.applyEmail, applyEmail) || other.applyEmail == applyEmail)&&(identical(other.emailTrust, emailTrust) || other.emailTrust == emailTrust)&&(identical(other.applyUrl, applyUrl) || other.applyUrl == applyUrl)&&(identical(other.status, status) || other.status == status)&&(identical(other.source, source) || other.source == source));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,jobId,title,companyName,location,remoteType,salaryMin,salaryMax,experienceMin,experienceMax,description,const DeepCollectionEquality().hash(_skillsRequired),jobType,applyEmail,emailTrust,applyUrl,status,source);

@override
String toString() {
  return 'JobRecord(jobId: $jobId, title: $title, companyName: $companyName, location: $location, remoteType: $remoteType, salaryMin: $salaryMin, salaryMax: $salaryMax, experienceMin: $experienceMin, experienceMax: $experienceMax, description: $description, skillsRequired: $skillsRequired, jobType: $jobType, applyEmail: $applyEmail, emailTrust: $emailTrust, applyUrl: $applyUrl, status: $status, source: $source)';
}


}

/// @nodoc
abstract mixin class _$JobRecordCopyWith<$Res> implements $JobRecordCopyWith<$Res> {
  factory _$JobRecordCopyWith(_JobRecord value, $Res Function(_JobRecord) _then) = __$JobRecordCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'job_id') String jobId, String title,@JsonKey(name: 'company_name') String companyName, String location,@JsonKey(name: 'remote_type') String? remoteType,@JsonKey(name: 'salary_min') int? salaryMin,@JsonKey(name: 'salary_max') int? salaryMax,@JsonKey(name: 'experience_min') int? experienceMin,@JsonKey(name: 'experience_max') int? experienceMax, String? description,@JsonKey(name: 'skills_required') List<String> skillsRequired,@JsonKey(name: 'job_type') String? jobType,@JsonKey(name: 'apply_email') String? applyEmail,@JsonKey(name: 'email_trust') String emailTrust,@JsonKey(name: 'apply_url') String? applyUrl, String status, String? source
});




}
/// @nodoc
class __$JobRecordCopyWithImpl<$Res>
    implements _$JobRecordCopyWith<$Res> {
  __$JobRecordCopyWithImpl(this._self, this._then);

  final _JobRecord _self;
  final $Res Function(_JobRecord) _then;

/// Create a copy of JobRecord
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? jobId = null,Object? title = null,Object? companyName = null,Object? location = null,Object? remoteType = freezed,Object? salaryMin = freezed,Object? salaryMax = freezed,Object? experienceMin = freezed,Object? experienceMax = freezed,Object? description = freezed,Object? skillsRequired = null,Object? jobType = freezed,Object? applyEmail = freezed,Object? emailTrust = null,Object? applyUrl = freezed,Object? status = null,Object? source = freezed,}) {
  return _then(_JobRecord(
jobId: null == jobId ? _self.jobId : jobId // ignore: cast_nullable_to_non_nullable
as String,title: null == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as String,companyName: null == companyName ? _self.companyName : companyName // ignore: cast_nullable_to_non_nullable
as String,location: null == location ? _self.location : location // ignore: cast_nullable_to_non_nullable
as String,remoteType: freezed == remoteType ? _self.remoteType : remoteType // ignore: cast_nullable_to_non_nullable
as String?,salaryMin: freezed == salaryMin ? _self.salaryMin : salaryMin // ignore: cast_nullable_to_non_nullable
as int?,salaryMax: freezed == salaryMax ? _self.salaryMax : salaryMax // ignore: cast_nullable_to_non_nullable
as int?,experienceMin: freezed == experienceMin ? _self.experienceMin : experienceMin // ignore: cast_nullable_to_non_nullable
as int?,experienceMax: freezed == experienceMax ? _self.experienceMax : experienceMax // ignore: cast_nullable_to_non_nullable
as int?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,skillsRequired: null == skillsRequired ? _self._skillsRequired : skillsRequired // ignore: cast_nullable_to_non_nullable
as List<String>,jobType: freezed == jobType ? _self.jobType : jobType // ignore: cast_nullable_to_non_nullable
as String?,applyEmail: freezed == applyEmail ? _self.applyEmail : applyEmail // ignore: cast_nullable_to_non_nullable
as String?,emailTrust: null == emailTrust ? _self.emailTrust : emailTrust // ignore: cast_nullable_to_non_nullable
as String,applyUrl: freezed == applyUrl ? _self.applyUrl : applyUrl // ignore: cast_nullable_to_non_nullable
as String?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,source: freezed == source ? _self.source : source // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$JobListResponse {

 List<JobRecord> get jobs; int get total; int get page;@JsonKey(name: 'page_size') int get pageSize;
/// Create a copy of JobListResponse
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$JobListResponseCopyWith<JobListResponse> get copyWith => _$JobListResponseCopyWithImpl<JobListResponse>(this as JobListResponse, _$identity);

  /// Serializes this JobListResponse to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is JobListResponse&&const DeepCollectionEquality().equals(other.jobs, jobs)&&(identical(other.total, total) || other.total == total)&&(identical(other.page, page) || other.page == page)&&(identical(other.pageSize, pageSize) || other.pageSize == pageSize));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(jobs),total,page,pageSize);

@override
String toString() {
  return 'JobListResponse(jobs: $jobs, total: $total, page: $page, pageSize: $pageSize)';
}


}

/// @nodoc
abstract mixin class $JobListResponseCopyWith<$Res>  {
  factory $JobListResponseCopyWith(JobListResponse value, $Res Function(JobListResponse) _then) = _$JobListResponseCopyWithImpl;
@useResult
$Res call({
 List<JobRecord> jobs, int total, int page,@JsonKey(name: 'page_size') int pageSize
});




}
/// @nodoc
class _$JobListResponseCopyWithImpl<$Res>
    implements $JobListResponseCopyWith<$Res> {
  _$JobListResponseCopyWithImpl(this._self, this._then);

  final JobListResponse _self;
  final $Res Function(JobListResponse) _then;

/// Create a copy of JobListResponse
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? jobs = null,Object? total = null,Object? page = null,Object? pageSize = null,}) {
  return _then(_self.copyWith(
jobs: null == jobs ? _self.jobs : jobs // ignore: cast_nullable_to_non_nullable
as List<JobRecord>,total: null == total ? _self.total : total // ignore: cast_nullable_to_non_nullable
as int,page: null == page ? _self.page : page // ignore: cast_nullable_to_non_nullable
as int,pageSize: null == pageSize ? _self.pageSize : pageSize // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [JobListResponse].
extension JobListResponsePatterns on JobListResponse {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _JobListResponse value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _JobListResponse() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _JobListResponse value)  $default,){
final _that = this;
switch (_that) {
case _JobListResponse():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _JobListResponse value)?  $default,){
final _that = this;
switch (_that) {
case _JobListResponse() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( List<JobRecord> jobs,  int total,  int page, @JsonKey(name: 'page_size')  int pageSize)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _JobListResponse() when $default != null:
return $default(_that.jobs,_that.total,_that.page,_that.pageSize);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( List<JobRecord> jobs,  int total,  int page, @JsonKey(name: 'page_size')  int pageSize)  $default,) {final _that = this;
switch (_that) {
case _JobListResponse():
return $default(_that.jobs,_that.total,_that.page,_that.pageSize);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( List<JobRecord> jobs,  int total,  int page, @JsonKey(name: 'page_size')  int pageSize)?  $default,) {final _that = this;
switch (_that) {
case _JobListResponse() when $default != null:
return $default(_that.jobs,_that.total,_that.page,_that.pageSize);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _JobListResponse implements JobListResponse {
  const _JobListResponse({required final  List<JobRecord> jobs, required this.total, required this.page, @JsonKey(name: 'page_size') required this.pageSize}): _jobs = jobs;
  factory _JobListResponse.fromJson(Map<String, dynamic> json) => _$JobListResponseFromJson(json);

 final  List<JobRecord> _jobs;
@override List<JobRecord> get jobs {
  if (_jobs is EqualUnmodifiableListView) return _jobs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_jobs);
}

@override final  int total;
@override final  int page;
@override@JsonKey(name: 'page_size') final  int pageSize;

/// Create a copy of JobListResponse
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$JobListResponseCopyWith<_JobListResponse> get copyWith => __$JobListResponseCopyWithImpl<_JobListResponse>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$JobListResponseToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _JobListResponse&&const DeepCollectionEquality().equals(other._jobs, _jobs)&&(identical(other.total, total) || other.total == total)&&(identical(other.page, page) || other.page == page)&&(identical(other.pageSize, pageSize) || other.pageSize == pageSize));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_jobs),total,page,pageSize);

@override
String toString() {
  return 'JobListResponse(jobs: $jobs, total: $total, page: $page, pageSize: $pageSize)';
}


}

/// @nodoc
abstract mixin class _$JobListResponseCopyWith<$Res> implements $JobListResponseCopyWith<$Res> {
  factory _$JobListResponseCopyWith(_JobListResponse value, $Res Function(_JobListResponse) _then) = __$JobListResponseCopyWithImpl;
@override @useResult
$Res call({
 List<JobRecord> jobs, int total, int page,@JsonKey(name: 'page_size') int pageSize
});




}
/// @nodoc
class __$JobListResponseCopyWithImpl<$Res>
    implements _$JobListResponseCopyWith<$Res> {
  __$JobListResponseCopyWithImpl(this._self, this._then);

  final _JobListResponse _self;
  final $Res Function(_JobListResponse) _then;

/// Create a copy of JobListResponse
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? jobs = null,Object? total = null,Object? page = null,Object? pageSize = null,}) {
  return _then(_JobListResponse(
jobs: null == jobs ? _self._jobs : jobs // ignore: cast_nullable_to_non_nullable
as List<JobRecord>,total: null == total ? _self.total : total // ignore: cast_nullable_to_non_nullable
as int,page: null == page ? _self.page : page // ignore: cast_nullable_to_non_nullable
as int,pageSize: null == pageSize ? _self.pageSize : pageSize // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$JobCountsResponse {

 int get total;@JsonKey(name: 'by_source') Map<String, int> get bySource;@JsonKey(name: 'by_status') Map<String, int> get byStatus;@JsonKey(name: 'by_email_trust') Map<String, int> get byEmailTrust;
/// Create a copy of JobCountsResponse
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$JobCountsResponseCopyWith<JobCountsResponse> get copyWith => _$JobCountsResponseCopyWithImpl<JobCountsResponse>(this as JobCountsResponse, _$identity);

  /// Serializes this JobCountsResponse to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is JobCountsResponse&&(identical(other.total, total) || other.total == total)&&const DeepCollectionEquality().equals(other.bySource, bySource)&&const DeepCollectionEquality().equals(other.byStatus, byStatus)&&const DeepCollectionEquality().equals(other.byEmailTrust, byEmailTrust));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,total,const DeepCollectionEquality().hash(bySource),const DeepCollectionEquality().hash(byStatus),const DeepCollectionEquality().hash(byEmailTrust));

@override
String toString() {
  return 'JobCountsResponse(total: $total, bySource: $bySource, byStatus: $byStatus, byEmailTrust: $byEmailTrust)';
}


}

/// @nodoc
abstract mixin class $JobCountsResponseCopyWith<$Res>  {
  factory $JobCountsResponseCopyWith(JobCountsResponse value, $Res Function(JobCountsResponse) _then) = _$JobCountsResponseCopyWithImpl;
@useResult
$Res call({
 int total,@JsonKey(name: 'by_source') Map<String, int> bySource,@JsonKey(name: 'by_status') Map<String, int> byStatus,@JsonKey(name: 'by_email_trust') Map<String, int> byEmailTrust
});




}
/// @nodoc
class _$JobCountsResponseCopyWithImpl<$Res>
    implements $JobCountsResponseCopyWith<$Res> {
  _$JobCountsResponseCopyWithImpl(this._self, this._then);

  final JobCountsResponse _self;
  final $Res Function(JobCountsResponse) _then;

/// Create a copy of JobCountsResponse
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? total = null,Object? bySource = null,Object? byStatus = null,Object? byEmailTrust = null,}) {
  return _then(_self.copyWith(
total: null == total ? _self.total : total // ignore: cast_nullable_to_non_nullable
as int,bySource: null == bySource ? _self.bySource : bySource // ignore: cast_nullable_to_non_nullable
as Map<String, int>,byStatus: null == byStatus ? _self.byStatus : byStatus // ignore: cast_nullable_to_non_nullable
as Map<String, int>,byEmailTrust: null == byEmailTrust ? _self.byEmailTrust : byEmailTrust // ignore: cast_nullable_to_non_nullable
as Map<String, int>,
  ));
}

}


/// Adds pattern-matching-related methods to [JobCountsResponse].
extension JobCountsResponsePatterns on JobCountsResponse {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _JobCountsResponse value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _JobCountsResponse() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _JobCountsResponse value)  $default,){
final _that = this;
switch (_that) {
case _JobCountsResponse():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _JobCountsResponse value)?  $default,){
final _that = this;
switch (_that) {
case _JobCountsResponse() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int total, @JsonKey(name: 'by_source')  Map<String, int> bySource, @JsonKey(name: 'by_status')  Map<String, int> byStatus, @JsonKey(name: 'by_email_trust')  Map<String, int> byEmailTrust)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _JobCountsResponse() when $default != null:
return $default(_that.total,_that.bySource,_that.byStatus,_that.byEmailTrust);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int total, @JsonKey(name: 'by_source')  Map<String, int> bySource, @JsonKey(name: 'by_status')  Map<String, int> byStatus, @JsonKey(name: 'by_email_trust')  Map<String, int> byEmailTrust)  $default,) {final _that = this;
switch (_that) {
case _JobCountsResponse():
return $default(_that.total,_that.bySource,_that.byStatus,_that.byEmailTrust);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int total, @JsonKey(name: 'by_source')  Map<String, int> bySource, @JsonKey(name: 'by_status')  Map<String, int> byStatus, @JsonKey(name: 'by_email_trust')  Map<String, int> byEmailTrust)?  $default,) {final _that = this;
switch (_that) {
case _JobCountsResponse() when $default != null:
return $default(_that.total,_that.bySource,_that.byStatus,_that.byEmailTrust);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _JobCountsResponse implements JobCountsResponse {
  const _JobCountsResponse({required this.total, @JsonKey(name: 'by_source') final  Map<String, int> bySource = const {}, @JsonKey(name: 'by_status') final  Map<String, int> byStatus = const {}, @JsonKey(name: 'by_email_trust') final  Map<String, int> byEmailTrust = const {}}): _bySource = bySource,_byStatus = byStatus,_byEmailTrust = byEmailTrust;
  factory _JobCountsResponse.fromJson(Map<String, dynamic> json) => _$JobCountsResponseFromJson(json);

@override final  int total;
 final  Map<String, int> _bySource;
@override@JsonKey(name: 'by_source') Map<String, int> get bySource {
  if (_bySource is EqualUnmodifiableMapView) return _bySource;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_bySource);
}

 final  Map<String, int> _byStatus;
@override@JsonKey(name: 'by_status') Map<String, int> get byStatus {
  if (_byStatus is EqualUnmodifiableMapView) return _byStatus;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_byStatus);
}

 final  Map<String, int> _byEmailTrust;
@override@JsonKey(name: 'by_email_trust') Map<String, int> get byEmailTrust {
  if (_byEmailTrust is EqualUnmodifiableMapView) return _byEmailTrust;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_byEmailTrust);
}


/// Create a copy of JobCountsResponse
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$JobCountsResponseCopyWith<_JobCountsResponse> get copyWith => __$JobCountsResponseCopyWithImpl<_JobCountsResponse>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$JobCountsResponseToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _JobCountsResponse&&(identical(other.total, total) || other.total == total)&&const DeepCollectionEquality().equals(other._bySource, _bySource)&&const DeepCollectionEquality().equals(other._byStatus, _byStatus)&&const DeepCollectionEquality().equals(other._byEmailTrust, _byEmailTrust));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,total,const DeepCollectionEquality().hash(_bySource),const DeepCollectionEquality().hash(_byStatus),const DeepCollectionEquality().hash(_byEmailTrust));

@override
String toString() {
  return 'JobCountsResponse(total: $total, bySource: $bySource, byStatus: $byStatus, byEmailTrust: $byEmailTrust)';
}


}

/// @nodoc
abstract mixin class _$JobCountsResponseCopyWith<$Res> implements $JobCountsResponseCopyWith<$Res> {
  factory _$JobCountsResponseCopyWith(_JobCountsResponse value, $Res Function(_JobCountsResponse) _then) = __$JobCountsResponseCopyWithImpl;
@override @useResult
$Res call({
 int total,@JsonKey(name: 'by_source') Map<String, int> bySource,@JsonKey(name: 'by_status') Map<String, int> byStatus,@JsonKey(name: 'by_email_trust') Map<String, int> byEmailTrust
});




}
/// @nodoc
class __$JobCountsResponseCopyWithImpl<$Res>
    implements _$JobCountsResponseCopyWith<$Res> {
  __$JobCountsResponseCopyWithImpl(this._self, this._then);

  final _JobCountsResponse _self;
  final $Res Function(_JobCountsResponse) _then;

/// Create a copy of JobCountsResponse
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? total = null,Object? bySource = null,Object? byStatus = null,Object? byEmailTrust = null,}) {
  return _then(_JobCountsResponse(
total: null == total ? _self.total : total // ignore: cast_nullable_to_non_nullable
as int,bySource: null == bySource ? _self._bySource : bySource // ignore: cast_nullable_to_non_nullable
as Map<String, int>,byStatus: null == byStatus ? _self._byStatus : byStatus // ignore: cast_nullable_to_non_nullable
as Map<String, int>,byEmailTrust: null == byEmailTrust ? _self._byEmailTrust : byEmailTrust // ignore: cast_nullable_to_non_nullable
as Map<String, int>,
  ));
}


}

// dart format on

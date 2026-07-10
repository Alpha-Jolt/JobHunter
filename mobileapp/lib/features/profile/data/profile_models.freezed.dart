// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'profile_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$UserExperience {

@JsonKey(name: 'exp_id') String? get expId;@JsonKey(name: 'job_title') String get jobTitle; String get company; String get location;@JsonKey(name: 'start_date') String get startDate;@JsonKey(name: 'end_date') String? get endDate;@JsonKey(name: 'is_current') bool get isCurrent; String? get description;
/// Create a copy of UserExperience
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UserExperienceCopyWith<UserExperience> get copyWith => _$UserExperienceCopyWithImpl<UserExperience>(this as UserExperience, _$identity);

  /// Serializes this UserExperience to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UserExperience&&(identical(other.expId, expId) || other.expId == expId)&&(identical(other.jobTitle, jobTitle) || other.jobTitle == jobTitle)&&(identical(other.company, company) || other.company == company)&&(identical(other.location, location) || other.location == location)&&(identical(other.startDate, startDate) || other.startDate == startDate)&&(identical(other.endDate, endDate) || other.endDate == endDate)&&(identical(other.isCurrent, isCurrent) || other.isCurrent == isCurrent)&&(identical(other.description, description) || other.description == description));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,expId,jobTitle,company,location,startDate,endDate,isCurrent,description);

@override
String toString() {
  return 'UserExperience(expId: $expId, jobTitle: $jobTitle, company: $company, location: $location, startDate: $startDate, endDate: $endDate, isCurrent: $isCurrent, description: $description)';
}


}

/// @nodoc
abstract mixin class $UserExperienceCopyWith<$Res>  {
  factory $UserExperienceCopyWith(UserExperience value, $Res Function(UserExperience) _then) = _$UserExperienceCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'exp_id') String? expId,@JsonKey(name: 'job_title') String jobTitle, String company, String location,@JsonKey(name: 'start_date') String startDate,@JsonKey(name: 'end_date') String? endDate,@JsonKey(name: 'is_current') bool isCurrent, String? description
});




}
/// @nodoc
class _$UserExperienceCopyWithImpl<$Res>
    implements $UserExperienceCopyWith<$Res> {
  _$UserExperienceCopyWithImpl(this._self, this._then);

  final UserExperience _self;
  final $Res Function(UserExperience) _then;

/// Create a copy of UserExperience
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? expId = freezed,Object? jobTitle = null,Object? company = null,Object? location = null,Object? startDate = null,Object? endDate = freezed,Object? isCurrent = null,Object? description = freezed,}) {
  return _then(_self.copyWith(
expId: freezed == expId ? _self.expId : expId // ignore: cast_nullable_to_non_nullable
as String?,jobTitle: null == jobTitle ? _self.jobTitle : jobTitle // ignore: cast_nullable_to_non_nullable
as String,company: null == company ? _self.company : company // ignore: cast_nullable_to_non_nullable
as String,location: null == location ? _self.location : location // ignore: cast_nullable_to_non_nullable
as String,startDate: null == startDate ? _self.startDate : startDate // ignore: cast_nullable_to_non_nullable
as String,endDate: freezed == endDate ? _self.endDate : endDate // ignore: cast_nullable_to_non_nullable
as String?,isCurrent: null == isCurrent ? _self.isCurrent : isCurrent // ignore: cast_nullable_to_non_nullable
as bool,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [UserExperience].
extension UserExperiencePatterns on UserExperience {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _UserExperience value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _UserExperience() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _UserExperience value)  $default,){
final _that = this;
switch (_that) {
case _UserExperience():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _UserExperience value)?  $default,){
final _that = this;
switch (_that) {
case _UserExperience() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'exp_id')  String? expId, @JsonKey(name: 'job_title')  String jobTitle,  String company,  String location, @JsonKey(name: 'start_date')  String startDate, @JsonKey(name: 'end_date')  String? endDate, @JsonKey(name: 'is_current')  bool isCurrent,  String? description)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _UserExperience() when $default != null:
return $default(_that.expId,_that.jobTitle,_that.company,_that.location,_that.startDate,_that.endDate,_that.isCurrent,_that.description);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'exp_id')  String? expId, @JsonKey(name: 'job_title')  String jobTitle,  String company,  String location, @JsonKey(name: 'start_date')  String startDate, @JsonKey(name: 'end_date')  String? endDate, @JsonKey(name: 'is_current')  bool isCurrent,  String? description)  $default,) {final _that = this;
switch (_that) {
case _UserExperience():
return $default(_that.expId,_that.jobTitle,_that.company,_that.location,_that.startDate,_that.endDate,_that.isCurrent,_that.description);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'exp_id')  String? expId, @JsonKey(name: 'job_title')  String jobTitle,  String company,  String location, @JsonKey(name: 'start_date')  String startDate, @JsonKey(name: 'end_date')  String? endDate, @JsonKey(name: 'is_current')  bool isCurrent,  String? description)?  $default,) {final _that = this;
switch (_that) {
case _UserExperience() when $default != null:
return $default(_that.expId,_that.jobTitle,_that.company,_that.location,_that.startDate,_that.endDate,_that.isCurrent,_that.description);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _UserExperience implements UserExperience {
  const _UserExperience({@JsonKey(name: 'exp_id') this.expId, @JsonKey(name: 'job_title') required this.jobTitle, required this.company, required this.location, @JsonKey(name: 'start_date') required this.startDate, @JsonKey(name: 'end_date') this.endDate, @JsonKey(name: 'is_current') this.isCurrent = false, this.description});
  factory _UserExperience.fromJson(Map<String, dynamic> json) => _$UserExperienceFromJson(json);

@override@JsonKey(name: 'exp_id') final  String? expId;
@override@JsonKey(name: 'job_title') final  String jobTitle;
@override final  String company;
@override final  String location;
@override@JsonKey(name: 'start_date') final  String startDate;
@override@JsonKey(name: 'end_date') final  String? endDate;
@override@JsonKey(name: 'is_current') final  bool isCurrent;
@override final  String? description;

/// Create a copy of UserExperience
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$UserExperienceCopyWith<_UserExperience> get copyWith => __$UserExperienceCopyWithImpl<_UserExperience>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$UserExperienceToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _UserExperience&&(identical(other.expId, expId) || other.expId == expId)&&(identical(other.jobTitle, jobTitle) || other.jobTitle == jobTitle)&&(identical(other.company, company) || other.company == company)&&(identical(other.location, location) || other.location == location)&&(identical(other.startDate, startDate) || other.startDate == startDate)&&(identical(other.endDate, endDate) || other.endDate == endDate)&&(identical(other.isCurrent, isCurrent) || other.isCurrent == isCurrent)&&(identical(other.description, description) || other.description == description));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,expId,jobTitle,company,location,startDate,endDate,isCurrent,description);

@override
String toString() {
  return 'UserExperience(expId: $expId, jobTitle: $jobTitle, company: $company, location: $location, startDate: $startDate, endDate: $endDate, isCurrent: $isCurrent, description: $description)';
}


}

/// @nodoc
abstract mixin class _$UserExperienceCopyWith<$Res> implements $UserExperienceCopyWith<$Res> {
  factory _$UserExperienceCopyWith(_UserExperience value, $Res Function(_UserExperience) _then) = __$UserExperienceCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'exp_id') String? expId,@JsonKey(name: 'job_title') String jobTitle, String company, String location,@JsonKey(name: 'start_date') String startDate,@JsonKey(name: 'end_date') String? endDate,@JsonKey(name: 'is_current') bool isCurrent, String? description
});




}
/// @nodoc
class __$UserExperienceCopyWithImpl<$Res>
    implements _$UserExperienceCopyWith<$Res> {
  __$UserExperienceCopyWithImpl(this._self, this._then);

  final _UserExperience _self;
  final $Res Function(_UserExperience) _then;

/// Create a copy of UserExperience
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? expId = freezed,Object? jobTitle = null,Object? company = null,Object? location = null,Object? startDate = null,Object? endDate = freezed,Object? isCurrent = null,Object? description = freezed,}) {
  return _then(_UserExperience(
expId: freezed == expId ? _self.expId : expId // ignore: cast_nullable_to_non_nullable
as String?,jobTitle: null == jobTitle ? _self.jobTitle : jobTitle // ignore: cast_nullable_to_non_nullable
as String,company: null == company ? _self.company : company // ignore: cast_nullable_to_non_nullable
as String,location: null == location ? _self.location : location // ignore: cast_nullable_to_non_nullable
as String,startDate: null == startDate ? _self.startDate : startDate // ignore: cast_nullable_to_non_nullable
as String,endDate: freezed == endDate ? _self.endDate : endDate // ignore: cast_nullable_to_non_nullable
as String?,isCurrent: null == isCurrent ? _self.isCurrent : isCurrent // ignore: cast_nullable_to_non_nullable
as bool,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$UserEducation {

@JsonKey(name: 'edu_id') String? get eduId; String get institution; String get degree;@JsonKey(name: 'field_of_study') String? get fieldOfStudy;@JsonKey(name: 'start_year') int get startYear;@JsonKey(name: 'end_year') int? get endYear;@JsonKey(name: 'is_current') bool get isCurrent; double? get gpa;
/// Create a copy of UserEducation
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UserEducationCopyWith<UserEducation> get copyWith => _$UserEducationCopyWithImpl<UserEducation>(this as UserEducation, _$identity);

  /// Serializes this UserEducation to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UserEducation&&(identical(other.eduId, eduId) || other.eduId == eduId)&&(identical(other.institution, institution) || other.institution == institution)&&(identical(other.degree, degree) || other.degree == degree)&&(identical(other.fieldOfStudy, fieldOfStudy) || other.fieldOfStudy == fieldOfStudy)&&(identical(other.startYear, startYear) || other.startYear == startYear)&&(identical(other.endYear, endYear) || other.endYear == endYear)&&(identical(other.isCurrent, isCurrent) || other.isCurrent == isCurrent)&&(identical(other.gpa, gpa) || other.gpa == gpa));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,eduId,institution,degree,fieldOfStudy,startYear,endYear,isCurrent,gpa);

@override
String toString() {
  return 'UserEducation(eduId: $eduId, institution: $institution, degree: $degree, fieldOfStudy: $fieldOfStudy, startYear: $startYear, endYear: $endYear, isCurrent: $isCurrent, gpa: $gpa)';
}


}

/// @nodoc
abstract mixin class $UserEducationCopyWith<$Res>  {
  factory $UserEducationCopyWith(UserEducation value, $Res Function(UserEducation) _then) = _$UserEducationCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'edu_id') String? eduId, String institution, String degree,@JsonKey(name: 'field_of_study') String? fieldOfStudy,@JsonKey(name: 'start_year') int startYear,@JsonKey(name: 'end_year') int? endYear,@JsonKey(name: 'is_current') bool isCurrent, double? gpa
});




}
/// @nodoc
class _$UserEducationCopyWithImpl<$Res>
    implements $UserEducationCopyWith<$Res> {
  _$UserEducationCopyWithImpl(this._self, this._then);

  final UserEducation _self;
  final $Res Function(UserEducation) _then;

/// Create a copy of UserEducation
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? eduId = freezed,Object? institution = null,Object? degree = null,Object? fieldOfStudy = freezed,Object? startYear = null,Object? endYear = freezed,Object? isCurrent = null,Object? gpa = freezed,}) {
  return _then(_self.copyWith(
eduId: freezed == eduId ? _self.eduId : eduId // ignore: cast_nullable_to_non_nullable
as String?,institution: null == institution ? _self.institution : institution // ignore: cast_nullable_to_non_nullable
as String,degree: null == degree ? _self.degree : degree // ignore: cast_nullable_to_non_nullable
as String,fieldOfStudy: freezed == fieldOfStudy ? _self.fieldOfStudy : fieldOfStudy // ignore: cast_nullable_to_non_nullable
as String?,startYear: null == startYear ? _self.startYear : startYear // ignore: cast_nullable_to_non_nullable
as int,endYear: freezed == endYear ? _self.endYear : endYear // ignore: cast_nullable_to_non_nullable
as int?,isCurrent: null == isCurrent ? _self.isCurrent : isCurrent // ignore: cast_nullable_to_non_nullable
as bool,gpa: freezed == gpa ? _self.gpa : gpa // ignore: cast_nullable_to_non_nullable
as double?,
  ));
}

}


/// Adds pattern-matching-related methods to [UserEducation].
extension UserEducationPatterns on UserEducation {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _UserEducation value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _UserEducation() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _UserEducation value)  $default,){
final _that = this;
switch (_that) {
case _UserEducation():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _UserEducation value)?  $default,){
final _that = this;
switch (_that) {
case _UserEducation() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'edu_id')  String? eduId,  String institution,  String degree, @JsonKey(name: 'field_of_study')  String? fieldOfStudy, @JsonKey(name: 'start_year')  int startYear, @JsonKey(name: 'end_year')  int? endYear, @JsonKey(name: 'is_current')  bool isCurrent,  double? gpa)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _UserEducation() when $default != null:
return $default(_that.eduId,_that.institution,_that.degree,_that.fieldOfStudy,_that.startYear,_that.endYear,_that.isCurrent,_that.gpa);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'edu_id')  String? eduId,  String institution,  String degree, @JsonKey(name: 'field_of_study')  String? fieldOfStudy, @JsonKey(name: 'start_year')  int startYear, @JsonKey(name: 'end_year')  int? endYear, @JsonKey(name: 'is_current')  bool isCurrent,  double? gpa)  $default,) {final _that = this;
switch (_that) {
case _UserEducation():
return $default(_that.eduId,_that.institution,_that.degree,_that.fieldOfStudy,_that.startYear,_that.endYear,_that.isCurrent,_that.gpa);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'edu_id')  String? eduId,  String institution,  String degree, @JsonKey(name: 'field_of_study')  String? fieldOfStudy, @JsonKey(name: 'start_year')  int startYear, @JsonKey(name: 'end_year')  int? endYear, @JsonKey(name: 'is_current')  bool isCurrent,  double? gpa)?  $default,) {final _that = this;
switch (_that) {
case _UserEducation() when $default != null:
return $default(_that.eduId,_that.institution,_that.degree,_that.fieldOfStudy,_that.startYear,_that.endYear,_that.isCurrent,_that.gpa);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _UserEducation implements UserEducation {
  const _UserEducation({@JsonKey(name: 'edu_id') this.eduId, required this.institution, required this.degree, @JsonKey(name: 'field_of_study') this.fieldOfStudy, @JsonKey(name: 'start_year') required this.startYear, @JsonKey(name: 'end_year') this.endYear, @JsonKey(name: 'is_current') this.isCurrent = false, this.gpa});
  factory _UserEducation.fromJson(Map<String, dynamic> json) => _$UserEducationFromJson(json);

@override@JsonKey(name: 'edu_id') final  String? eduId;
@override final  String institution;
@override final  String degree;
@override@JsonKey(name: 'field_of_study') final  String? fieldOfStudy;
@override@JsonKey(name: 'start_year') final  int startYear;
@override@JsonKey(name: 'end_year') final  int? endYear;
@override@JsonKey(name: 'is_current') final  bool isCurrent;
@override final  double? gpa;

/// Create a copy of UserEducation
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$UserEducationCopyWith<_UserEducation> get copyWith => __$UserEducationCopyWithImpl<_UserEducation>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$UserEducationToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _UserEducation&&(identical(other.eduId, eduId) || other.eduId == eduId)&&(identical(other.institution, institution) || other.institution == institution)&&(identical(other.degree, degree) || other.degree == degree)&&(identical(other.fieldOfStudy, fieldOfStudy) || other.fieldOfStudy == fieldOfStudy)&&(identical(other.startYear, startYear) || other.startYear == startYear)&&(identical(other.endYear, endYear) || other.endYear == endYear)&&(identical(other.isCurrent, isCurrent) || other.isCurrent == isCurrent)&&(identical(other.gpa, gpa) || other.gpa == gpa));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,eduId,institution,degree,fieldOfStudy,startYear,endYear,isCurrent,gpa);

@override
String toString() {
  return 'UserEducation(eduId: $eduId, institution: $institution, degree: $degree, fieldOfStudy: $fieldOfStudy, startYear: $startYear, endYear: $endYear, isCurrent: $isCurrent, gpa: $gpa)';
}


}

/// @nodoc
abstract mixin class _$UserEducationCopyWith<$Res> implements $UserEducationCopyWith<$Res> {
  factory _$UserEducationCopyWith(_UserEducation value, $Res Function(_UserEducation) _then) = __$UserEducationCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'edu_id') String? eduId, String institution, String degree,@JsonKey(name: 'field_of_study') String? fieldOfStudy,@JsonKey(name: 'start_year') int startYear,@JsonKey(name: 'end_year') int? endYear,@JsonKey(name: 'is_current') bool isCurrent, double? gpa
});




}
/// @nodoc
class __$UserEducationCopyWithImpl<$Res>
    implements _$UserEducationCopyWith<$Res> {
  __$UserEducationCopyWithImpl(this._self, this._then);

  final _UserEducation _self;
  final $Res Function(_UserEducation) _then;

/// Create a copy of UserEducation
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? eduId = freezed,Object? institution = null,Object? degree = null,Object? fieldOfStudy = freezed,Object? startYear = null,Object? endYear = freezed,Object? isCurrent = null,Object? gpa = freezed,}) {
  return _then(_UserEducation(
eduId: freezed == eduId ? _self.eduId : eduId // ignore: cast_nullable_to_non_nullable
as String?,institution: null == institution ? _self.institution : institution // ignore: cast_nullable_to_non_nullable
as String,degree: null == degree ? _self.degree : degree // ignore: cast_nullable_to_non_nullable
as String,fieldOfStudy: freezed == fieldOfStudy ? _self.fieldOfStudy : fieldOfStudy // ignore: cast_nullable_to_non_nullable
as String?,startYear: null == startYear ? _self.startYear : startYear // ignore: cast_nullable_to_non_nullable
as int,endYear: freezed == endYear ? _self.endYear : endYear // ignore: cast_nullable_to_non_nullable
as int?,isCurrent: null == isCurrent ? _self.isCurrent : isCurrent // ignore: cast_nullable_to_non_nullable
as bool,gpa: freezed == gpa ? _self.gpa : gpa // ignore: cast_nullable_to_non_nullable
as double?,
  ));
}


}


/// @nodoc
mixin _$UserProject {

@JsonKey(name: 'proj_id') String? get projId; String get name; String? get description;@JsonKey(name: 'tech_stack') List<String> get techStack;@JsonKey(name: 'project_url') String? get projectUrl;@JsonKey(name: 'start_date') String? get startDate;@JsonKey(name: 'end_date') String? get endDate;
/// Create a copy of UserProject
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UserProjectCopyWith<UserProject> get copyWith => _$UserProjectCopyWithImpl<UserProject>(this as UserProject, _$identity);

  /// Serializes this UserProject to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UserProject&&(identical(other.projId, projId) || other.projId == projId)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other.techStack, techStack)&&(identical(other.projectUrl, projectUrl) || other.projectUrl == projectUrl)&&(identical(other.startDate, startDate) || other.startDate == startDate)&&(identical(other.endDate, endDate) || other.endDate == endDate));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,projId,name,description,const DeepCollectionEquality().hash(techStack),projectUrl,startDate,endDate);

@override
String toString() {
  return 'UserProject(projId: $projId, name: $name, description: $description, techStack: $techStack, projectUrl: $projectUrl, startDate: $startDate, endDate: $endDate)';
}


}

/// @nodoc
abstract mixin class $UserProjectCopyWith<$Res>  {
  factory $UserProjectCopyWith(UserProject value, $Res Function(UserProject) _then) = _$UserProjectCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'proj_id') String? projId, String name, String? description,@JsonKey(name: 'tech_stack') List<String> techStack,@JsonKey(name: 'project_url') String? projectUrl,@JsonKey(name: 'start_date') String? startDate,@JsonKey(name: 'end_date') String? endDate
});




}
/// @nodoc
class _$UserProjectCopyWithImpl<$Res>
    implements $UserProjectCopyWith<$Res> {
  _$UserProjectCopyWithImpl(this._self, this._then);

  final UserProject _self;
  final $Res Function(UserProject) _then;

/// Create a copy of UserProject
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? projId = freezed,Object? name = null,Object? description = freezed,Object? techStack = null,Object? projectUrl = freezed,Object? startDate = freezed,Object? endDate = freezed,}) {
  return _then(_self.copyWith(
projId: freezed == projId ? _self.projId : projId // ignore: cast_nullable_to_non_nullable
as String?,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,techStack: null == techStack ? _self.techStack : techStack // ignore: cast_nullable_to_non_nullable
as List<String>,projectUrl: freezed == projectUrl ? _self.projectUrl : projectUrl // ignore: cast_nullable_to_non_nullable
as String?,startDate: freezed == startDate ? _self.startDate : startDate // ignore: cast_nullable_to_non_nullable
as String?,endDate: freezed == endDate ? _self.endDate : endDate // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [UserProject].
extension UserProjectPatterns on UserProject {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _UserProject value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _UserProject() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _UserProject value)  $default,){
final _that = this;
switch (_that) {
case _UserProject():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _UserProject value)?  $default,){
final _that = this;
switch (_that) {
case _UserProject() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'proj_id')  String? projId,  String name,  String? description, @JsonKey(name: 'tech_stack')  List<String> techStack, @JsonKey(name: 'project_url')  String? projectUrl, @JsonKey(name: 'start_date')  String? startDate, @JsonKey(name: 'end_date')  String? endDate)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _UserProject() when $default != null:
return $default(_that.projId,_that.name,_that.description,_that.techStack,_that.projectUrl,_that.startDate,_that.endDate);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'proj_id')  String? projId,  String name,  String? description, @JsonKey(name: 'tech_stack')  List<String> techStack, @JsonKey(name: 'project_url')  String? projectUrl, @JsonKey(name: 'start_date')  String? startDate, @JsonKey(name: 'end_date')  String? endDate)  $default,) {final _that = this;
switch (_that) {
case _UserProject():
return $default(_that.projId,_that.name,_that.description,_that.techStack,_that.projectUrl,_that.startDate,_that.endDate);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'proj_id')  String? projId,  String name,  String? description, @JsonKey(name: 'tech_stack')  List<String> techStack, @JsonKey(name: 'project_url')  String? projectUrl, @JsonKey(name: 'start_date')  String? startDate, @JsonKey(name: 'end_date')  String? endDate)?  $default,) {final _that = this;
switch (_that) {
case _UserProject() when $default != null:
return $default(_that.projId,_that.name,_that.description,_that.techStack,_that.projectUrl,_that.startDate,_that.endDate);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _UserProject implements UserProject {
  const _UserProject({@JsonKey(name: 'proj_id') this.projId, required this.name, this.description, @JsonKey(name: 'tech_stack') final  List<String> techStack = const [], @JsonKey(name: 'project_url') this.projectUrl, @JsonKey(name: 'start_date') this.startDate, @JsonKey(name: 'end_date') this.endDate}): _techStack = techStack;
  factory _UserProject.fromJson(Map<String, dynamic> json) => _$UserProjectFromJson(json);

@override@JsonKey(name: 'proj_id') final  String? projId;
@override final  String name;
@override final  String? description;
 final  List<String> _techStack;
@override@JsonKey(name: 'tech_stack') List<String> get techStack {
  if (_techStack is EqualUnmodifiableListView) return _techStack;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_techStack);
}

@override@JsonKey(name: 'project_url') final  String? projectUrl;
@override@JsonKey(name: 'start_date') final  String? startDate;
@override@JsonKey(name: 'end_date') final  String? endDate;

/// Create a copy of UserProject
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$UserProjectCopyWith<_UserProject> get copyWith => __$UserProjectCopyWithImpl<_UserProject>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$UserProjectToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _UserProject&&(identical(other.projId, projId) || other.projId == projId)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other._techStack, _techStack)&&(identical(other.projectUrl, projectUrl) || other.projectUrl == projectUrl)&&(identical(other.startDate, startDate) || other.startDate == startDate)&&(identical(other.endDate, endDate) || other.endDate == endDate));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,projId,name,description,const DeepCollectionEquality().hash(_techStack),projectUrl,startDate,endDate);

@override
String toString() {
  return 'UserProject(projId: $projId, name: $name, description: $description, techStack: $techStack, projectUrl: $projectUrl, startDate: $startDate, endDate: $endDate)';
}


}

/// @nodoc
abstract mixin class _$UserProjectCopyWith<$Res> implements $UserProjectCopyWith<$Res> {
  factory _$UserProjectCopyWith(_UserProject value, $Res Function(_UserProject) _then) = __$UserProjectCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'proj_id') String? projId, String name, String? description,@JsonKey(name: 'tech_stack') List<String> techStack,@JsonKey(name: 'project_url') String? projectUrl,@JsonKey(name: 'start_date') String? startDate,@JsonKey(name: 'end_date') String? endDate
});




}
/// @nodoc
class __$UserProjectCopyWithImpl<$Res>
    implements _$UserProjectCopyWith<$Res> {
  __$UserProjectCopyWithImpl(this._self, this._then);

  final _UserProject _self;
  final $Res Function(_UserProject) _then;

/// Create a copy of UserProject
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? projId = freezed,Object? name = null,Object? description = freezed,Object? techStack = null,Object? projectUrl = freezed,Object? startDate = freezed,Object? endDate = freezed,}) {
  return _then(_UserProject(
projId: freezed == projId ? _self.projId : projId // ignore: cast_nullable_to_non_nullable
as String?,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,techStack: null == techStack ? _self._techStack : techStack // ignore: cast_nullable_to_non_nullable
as List<String>,projectUrl: freezed == projectUrl ? _self.projectUrl : projectUrl // ignore: cast_nullable_to_non_nullable
as String?,startDate: freezed == startDate ? _self.startDate : startDate // ignore: cast_nullable_to_non_nullable
as String?,endDate: freezed == endDate ? _self.endDate : endDate // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$UserSkill {

 String get name; String? get level;
/// Create a copy of UserSkill
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UserSkillCopyWith<UserSkill> get copyWith => _$UserSkillCopyWithImpl<UserSkill>(this as UserSkill, _$identity);

  /// Serializes this UserSkill to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UserSkill&&(identical(other.name, name) || other.name == name)&&(identical(other.level, level) || other.level == level));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,level);

@override
String toString() {
  return 'UserSkill(name: $name, level: $level)';
}


}

/// @nodoc
abstract mixin class $UserSkillCopyWith<$Res>  {
  factory $UserSkillCopyWith(UserSkill value, $Res Function(UserSkill) _then) = _$UserSkillCopyWithImpl;
@useResult
$Res call({
 String name, String? level
});




}
/// @nodoc
class _$UserSkillCopyWithImpl<$Res>
    implements $UserSkillCopyWith<$Res> {
  _$UserSkillCopyWithImpl(this._self, this._then);

  final UserSkill _self;
  final $Res Function(UserSkill) _then;

/// Create a copy of UserSkill
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = null,Object? level = freezed,}) {
  return _then(_self.copyWith(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,level: freezed == level ? _self.level : level // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [UserSkill].
extension UserSkillPatterns on UserSkill {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _UserSkill value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _UserSkill() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _UserSkill value)  $default,){
final _that = this;
switch (_that) {
case _UserSkill():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _UserSkill value)?  $default,){
final _that = this;
switch (_that) {
case _UserSkill() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String name,  String? level)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _UserSkill() when $default != null:
return $default(_that.name,_that.level);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String name,  String? level)  $default,) {final _that = this;
switch (_that) {
case _UserSkill():
return $default(_that.name,_that.level);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String name,  String? level)?  $default,) {final _that = this;
switch (_that) {
case _UserSkill() when $default != null:
return $default(_that.name,_that.level);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _UserSkill implements UserSkill {
  const _UserSkill({required this.name, this.level});
  factory _UserSkill.fromJson(Map<String, dynamic> json) => _$UserSkillFromJson(json);

@override final  String name;
@override final  String? level;

/// Create a copy of UserSkill
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$UserSkillCopyWith<_UserSkill> get copyWith => __$UserSkillCopyWithImpl<_UserSkill>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$UserSkillToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _UserSkill&&(identical(other.name, name) || other.name == name)&&(identical(other.level, level) || other.level == level));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,level);

@override
String toString() {
  return 'UserSkill(name: $name, level: $level)';
}


}

/// @nodoc
abstract mixin class _$UserSkillCopyWith<$Res> implements $UserSkillCopyWith<$Res> {
  factory _$UserSkillCopyWith(_UserSkill value, $Res Function(_UserSkill) _then) = __$UserSkillCopyWithImpl;
@override @useResult
$Res call({
 String name, String? level
});




}
/// @nodoc
class __$UserSkillCopyWithImpl<$Res>
    implements _$UserSkillCopyWith<$Res> {
  __$UserSkillCopyWithImpl(this._self, this._then);

  final _UserSkill _self;
  final $Res Function(_UserSkill) _then;

/// Create a copy of UserSkill
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = null,Object? level = freezed,}) {
  return _then(_UserSkill(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,level: freezed == level ? _self.level : level // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$UserCertification {

 String get name; String? get issuer;@JsonKey(name: 'issued_date') String? get issuedDate;@JsonKey(name: 'credential_url') String? get credentialUrl;
/// Create a copy of UserCertification
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UserCertificationCopyWith<UserCertification> get copyWith => _$UserCertificationCopyWithImpl<UserCertification>(this as UserCertification, _$identity);

  /// Serializes this UserCertification to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UserCertification&&(identical(other.name, name) || other.name == name)&&(identical(other.issuer, issuer) || other.issuer == issuer)&&(identical(other.issuedDate, issuedDate) || other.issuedDate == issuedDate)&&(identical(other.credentialUrl, credentialUrl) || other.credentialUrl == credentialUrl));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,issuer,issuedDate,credentialUrl);

@override
String toString() {
  return 'UserCertification(name: $name, issuer: $issuer, issuedDate: $issuedDate, credentialUrl: $credentialUrl)';
}


}

/// @nodoc
abstract mixin class $UserCertificationCopyWith<$Res>  {
  factory $UserCertificationCopyWith(UserCertification value, $Res Function(UserCertification) _then) = _$UserCertificationCopyWithImpl;
@useResult
$Res call({
 String name, String? issuer,@JsonKey(name: 'issued_date') String? issuedDate,@JsonKey(name: 'credential_url') String? credentialUrl
});




}
/// @nodoc
class _$UserCertificationCopyWithImpl<$Res>
    implements $UserCertificationCopyWith<$Res> {
  _$UserCertificationCopyWithImpl(this._self, this._then);

  final UserCertification _self;
  final $Res Function(UserCertification) _then;

/// Create a copy of UserCertification
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = null,Object? issuer = freezed,Object? issuedDate = freezed,Object? credentialUrl = freezed,}) {
  return _then(_self.copyWith(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,issuer: freezed == issuer ? _self.issuer : issuer // ignore: cast_nullable_to_non_nullable
as String?,issuedDate: freezed == issuedDate ? _self.issuedDate : issuedDate // ignore: cast_nullable_to_non_nullable
as String?,credentialUrl: freezed == credentialUrl ? _self.credentialUrl : credentialUrl // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [UserCertification].
extension UserCertificationPatterns on UserCertification {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _UserCertification value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _UserCertification() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _UserCertification value)  $default,){
final _that = this;
switch (_that) {
case _UserCertification():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _UserCertification value)?  $default,){
final _that = this;
switch (_that) {
case _UserCertification() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String name,  String? issuer, @JsonKey(name: 'issued_date')  String? issuedDate, @JsonKey(name: 'credential_url')  String? credentialUrl)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _UserCertification() when $default != null:
return $default(_that.name,_that.issuer,_that.issuedDate,_that.credentialUrl);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String name,  String? issuer, @JsonKey(name: 'issued_date')  String? issuedDate, @JsonKey(name: 'credential_url')  String? credentialUrl)  $default,) {final _that = this;
switch (_that) {
case _UserCertification():
return $default(_that.name,_that.issuer,_that.issuedDate,_that.credentialUrl);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String name,  String? issuer, @JsonKey(name: 'issued_date')  String? issuedDate, @JsonKey(name: 'credential_url')  String? credentialUrl)?  $default,) {final _that = this;
switch (_that) {
case _UserCertification() when $default != null:
return $default(_that.name,_that.issuer,_that.issuedDate,_that.credentialUrl);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _UserCertification implements UserCertification {
  const _UserCertification({required this.name, this.issuer, @JsonKey(name: 'issued_date') this.issuedDate, @JsonKey(name: 'credential_url') this.credentialUrl});
  factory _UserCertification.fromJson(Map<String, dynamic> json) => _$UserCertificationFromJson(json);

@override final  String name;
@override final  String? issuer;
@override@JsonKey(name: 'issued_date') final  String? issuedDate;
@override@JsonKey(name: 'credential_url') final  String? credentialUrl;

/// Create a copy of UserCertification
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$UserCertificationCopyWith<_UserCertification> get copyWith => __$UserCertificationCopyWithImpl<_UserCertification>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$UserCertificationToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _UserCertification&&(identical(other.name, name) || other.name == name)&&(identical(other.issuer, issuer) || other.issuer == issuer)&&(identical(other.issuedDate, issuedDate) || other.issuedDate == issuedDate)&&(identical(other.credentialUrl, credentialUrl) || other.credentialUrl == credentialUrl));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,issuer,issuedDate,credentialUrl);

@override
String toString() {
  return 'UserCertification(name: $name, issuer: $issuer, issuedDate: $issuedDate, credentialUrl: $credentialUrl)';
}


}

/// @nodoc
abstract mixin class _$UserCertificationCopyWith<$Res> implements $UserCertificationCopyWith<$Res> {
  factory _$UserCertificationCopyWith(_UserCertification value, $Res Function(_UserCertification) _then) = __$UserCertificationCopyWithImpl;
@override @useResult
$Res call({
 String name, String? issuer,@JsonKey(name: 'issued_date') String? issuedDate,@JsonKey(name: 'credential_url') String? credentialUrl
});




}
/// @nodoc
class __$UserCertificationCopyWithImpl<$Res>
    implements _$UserCertificationCopyWith<$Res> {
  __$UserCertificationCopyWithImpl(this._self, this._then);

  final _UserCertification _self;
  final $Res Function(_UserCertification) _then;

/// Create a copy of UserCertification
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = null,Object? issuer = freezed,Object? issuedDate = freezed,Object? credentialUrl = freezed,}) {
  return _then(_UserCertification(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,issuer: freezed == issuer ? _self.issuer : issuer // ignore: cast_nullable_to_non_nullable
as String?,issuedDate: freezed == issuedDate ? _self.issuedDate : issuedDate // ignore: cast_nullable_to_non_nullable
as String?,credentialUrl: freezed == credentialUrl ? _self.credentialUrl : credentialUrl // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$UserLanguage {

 String get name; String? get proficiency;
/// Create a copy of UserLanguage
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UserLanguageCopyWith<UserLanguage> get copyWith => _$UserLanguageCopyWithImpl<UserLanguage>(this as UserLanguage, _$identity);

  /// Serializes this UserLanguage to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UserLanguage&&(identical(other.name, name) || other.name == name)&&(identical(other.proficiency, proficiency) || other.proficiency == proficiency));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,proficiency);

@override
String toString() {
  return 'UserLanguage(name: $name, proficiency: $proficiency)';
}


}

/// @nodoc
abstract mixin class $UserLanguageCopyWith<$Res>  {
  factory $UserLanguageCopyWith(UserLanguage value, $Res Function(UserLanguage) _then) = _$UserLanguageCopyWithImpl;
@useResult
$Res call({
 String name, String? proficiency
});




}
/// @nodoc
class _$UserLanguageCopyWithImpl<$Res>
    implements $UserLanguageCopyWith<$Res> {
  _$UserLanguageCopyWithImpl(this._self, this._then);

  final UserLanguage _self;
  final $Res Function(UserLanguage) _then;

/// Create a copy of UserLanguage
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = null,Object? proficiency = freezed,}) {
  return _then(_self.copyWith(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,proficiency: freezed == proficiency ? _self.proficiency : proficiency // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [UserLanguage].
extension UserLanguagePatterns on UserLanguage {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _UserLanguage value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _UserLanguage() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _UserLanguage value)  $default,){
final _that = this;
switch (_that) {
case _UserLanguage():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _UserLanguage value)?  $default,){
final _that = this;
switch (_that) {
case _UserLanguage() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String name,  String? proficiency)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _UserLanguage() when $default != null:
return $default(_that.name,_that.proficiency);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String name,  String? proficiency)  $default,) {final _that = this;
switch (_that) {
case _UserLanguage():
return $default(_that.name,_that.proficiency);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String name,  String? proficiency)?  $default,) {final _that = this;
switch (_that) {
case _UserLanguage() when $default != null:
return $default(_that.name,_that.proficiency);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _UserLanguage implements UserLanguage {
  const _UserLanguage({required this.name, this.proficiency});
  factory _UserLanguage.fromJson(Map<String, dynamic> json) => _$UserLanguageFromJson(json);

@override final  String name;
@override final  String? proficiency;

/// Create a copy of UserLanguage
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$UserLanguageCopyWith<_UserLanguage> get copyWith => __$UserLanguageCopyWithImpl<_UserLanguage>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$UserLanguageToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _UserLanguage&&(identical(other.name, name) || other.name == name)&&(identical(other.proficiency, proficiency) || other.proficiency == proficiency));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,proficiency);

@override
String toString() {
  return 'UserLanguage(name: $name, proficiency: $proficiency)';
}


}

/// @nodoc
abstract mixin class _$UserLanguageCopyWith<$Res> implements $UserLanguageCopyWith<$Res> {
  factory _$UserLanguageCopyWith(_UserLanguage value, $Res Function(_UserLanguage) _then) = __$UserLanguageCopyWithImpl;
@override @useResult
$Res call({
 String name, String? proficiency
});




}
/// @nodoc
class __$UserLanguageCopyWithImpl<$Res>
    implements _$UserLanguageCopyWith<$Res> {
  __$UserLanguageCopyWithImpl(this._self, this._then);

  final _UserLanguage _self;
  final $Res Function(_UserLanguage) _then;

/// Create a copy of UserLanguage
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = null,Object? proficiency = freezed,}) {
  return _then(_UserLanguage(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,proficiency: freezed == proficiency ? _self.proficiency : proficiency // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$UserAchievement {

 String get title; String? get description; String? get date;
/// Create a copy of UserAchievement
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UserAchievementCopyWith<UserAchievement> get copyWith => _$UserAchievementCopyWithImpl<UserAchievement>(this as UserAchievement, _$identity);

  /// Serializes this UserAchievement to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UserAchievement&&(identical(other.title, title) || other.title == title)&&(identical(other.description, description) || other.description == description)&&(identical(other.date, date) || other.date == date));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,title,description,date);

@override
String toString() {
  return 'UserAchievement(title: $title, description: $description, date: $date)';
}


}

/// @nodoc
abstract mixin class $UserAchievementCopyWith<$Res>  {
  factory $UserAchievementCopyWith(UserAchievement value, $Res Function(UserAchievement) _then) = _$UserAchievementCopyWithImpl;
@useResult
$Res call({
 String title, String? description, String? date
});




}
/// @nodoc
class _$UserAchievementCopyWithImpl<$Res>
    implements $UserAchievementCopyWith<$Res> {
  _$UserAchievementCopyWithImpl(this._self, this._then);

  final UserAchievement _self;
  final $Res Function(UserAchievement) _then;

/// Create a copy of UserAchievement
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? title = null,Object? description = freezed,Object? date = freezed,}) {
  return _then(_self.copyWith(
title: null == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,date: freezed == date ? _self.date : date // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [UserAchievement].
extension UserAchievementPatterns on UserAchievement {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _UserAchievement value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _UserAchievement() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _UserAchievement value)  $default,){
final _that = this;
switch (_that) {
case _UserAchievement():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _UserAchievement value)?  $default,){
final _that = this;
switch (_that) {
case _UserAchievement() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String title,  String? description,  String? date)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _UserAchievement() when $default != null:
return $default(_that.title,_that.description,_that.date);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String title,  String? description,  String? date)  $default,) {final _that = this;
switch (_that) {
case _UserAchievement():
return $default(_that.title,_that.description,_that.date);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String title,  String? description,  String? date)?  $default,) {final _that = this;
switch (_that) {
case _UserAchievement() when $default != null:
return $default(_that.title,_that.description,_that.date);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _UserAchievement implements UserAchievement {
  const _UserAchievement({required this.title, this.description, this.date});
  factory _UserAchievement.fromJson(Map<String, dynamic> json) => _$UserAchievementFromJson(json);

@override final  String title;
@override final  String? description;
@override final  String? date;

/// Create a copy of UserAchievement
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$UserAchievementCopyWith<_UserAchievement> get copyWith => __$UserAchievementCopyWithImpl<_UserAchievement>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$UserAchievementToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _UserAchievement&&(identical(other.title, title) || other.title == title)&&(identical(other.description, description) || other.description == description)&&(identical(other.date, date) || other.date == date));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,title,description,date);

@override
String toString() {
  return 'UserAchievement(title: $title, description: $description, date: $date)';
}


}

/// @nodoc
abstract mixin class _$UserAchievementCopyWith<$Res> implements $UserAchievementCopyWith<$Res> {
  factory _$UserAchievementCopyWith(_UserAchievement value, $Res Function(_UserAchievement) _then) = __$UserAchievementCopyWithImpl;
@override @useResult
$Res call({
 String title, String? description, String? date
});




}
/// @nodoc
class __$UserAchievementCopyWithImpl<$Res>
    implements _$UserAchievementCopyWith<$Res> {
  __$UserAchievementCopyWithImpl(this._self, this._then);

  final _UserAchievement _self;
  final $Res Function(_UserAchievement) _then;

/// Create a copy of UserAchievement
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? title = null,Object? description = freezed,Object? date = freezed,}) {
  return _then(_UserAchievement(
title: null == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,date: freezed == date ? _self.date : date // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$UserSocialLink {

 String get platform; String get url;
/// Create a copy of UserSocialLink
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UserSocialLinkCopyWith<UserSocialLink> get copyWith => _$UserSocialLinkCopyWithImpl<UserSocialLink>(this as UserSocialLink, _$identity);

  /// Serializes this UserSocialLink to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UserSocialLink&&(identical(other.platform, platform) || other.platform == platform)&&(identical(other.url, url) || other.url == url));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,platform,url);

@override
String toString() {
  return 'UserSocialLink(platform: $platform, url: $url)';
}


}

/// @nodoc
abstract mixin class $UserSocialLinkCopyWith<$Res>  {
  factory $UserSocialLinkCopyWith(UserSocialLink value, $Res Function(UserSocialLink) _then) = _$UserSocialLinkCopyWithImpl;
@useResult
$Res call({
 String platform, String url
});




}
/// @nodoc
class _$UserSocialLinkCopyWithImpl<$Res>
    implements $UserSocialLinkCopyWith<$Res> {
  _$UserSocialLinkCopyWithImpl(this._self, this._then);

  final UserSocialLink _self;
  final $Res Function(UserSocialLink) _then;

/// Create a copy of UserSocialLink
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? platform = null,Object? url = null,}) {
  return _then(_self.copyWith(
platform: null == platform ? _self.platform : platform // ignore: cast_nullable_to_non_nullable
as String,url: null == url ? _self.url : url // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [UserSocialLink].
extension UserSocialLinkPatterns on UserSocialLink {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _UserSocialLink value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _UserSocialLink() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _UserSocialLink value)  $default,){
final _that = this;
switch (_that) {
case _UserSocialLink():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _UserSocialLink value)?  $default,){
final _that = this;
switch (_that) {
case _UserSocialLink() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String platform,  String url)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _UserSocialLink() when $default != null:
return $default(_that.platform,_that.url);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String platform,  String url)  $default,) {final _that = this;
switch (_that) {
case _UserSocialLink():
return $default(_that.platform,_that.url);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String platform,  String url)?  $default,) {final _that = this;
switch (_that) {
case _UserSocialLink() when $default != null:
return $default(_that.platform,_that.url);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _UserSocialLink implements UserSocialLink {
  const _UserSocialLink({required this.platform, required this.url});
  factory _UserSocialLink.fromJson(Map<String, dynamic> json) => _$UserSocialLinkFromJson(json);

@override final  String platform;
@override final  String url;

/// Create a copy of UserSocialLink
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$UserSocialLinkCopyWith<_UserSocialLink> get copyWith => __$UserSocialLinkCopyWithImpl<_UserSocialLink>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$UserSocialLinkToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _UserSocialLink&&(identical(other.platform, platform) || other.platform == platform)&&(identical(other.url, url) || other.url == url));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,platform,url);

@override
String toString() {
  return 'UserSocialLink(platform: $platform, url: $url)';
}


}

/// @nodoc
abstract mixin class _$UserSocialLinkCopyWith<$Res> implements $UserSocialLinkCopyWith<$Res> {
  factory _$UserSocialLinkCopyWith(_UserSocialLink value, $Res Function(_UserSocialLink) _then) = __$UserSocialLinkCopyWithImpl;
@override @useResult
$Res call({
 String platform, String url
});




}
/// @nodoc
class __$UserSocialLinkCopyWithImpl<$Res>
    implements _$UserSocialLinkCopyWith<$Res> {
  __$UserSocialLinkCopyWithImpl(this._self, this._then);

  final _UserSocialLink _self;
  final $Res Function(_UserSocialLink) _then;

/// Create a copy of UserSocialLink
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? platform = null,Object? url = null,}) {
  return _then(_UserSocialLink(
platform: null == platform ? _self.platform : platform // ignore: cast_nullable_to_non_nullable
as String,url: null == url ? _self.url : url // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$UserProfile {

@JsonKey(name: 'user_id') String get userId; String? get username; String? get headline; String? get bio; String? get location;@JsonKey(name: 'avatar_key') String? get avatarKey;@JsonKey(name: 'avatar_url') String? get avatarUrl;@JsonKey(name: 'is_public') bool get isPublic; List<UserExperience> get experiences; List<UserEducation> get education; List<UserProject> get projects; List<UserSkill> get skills; List<UserCertification> get certifications; List<UserLanguage> get languages; List<UserAchievement> get achievements;@JsonKey(name: 'social_links') List<UserSocialLink> get socialLinks;
/// Create a copy of UserProfile
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UserProfileCopyWith<UserProfile> get copyWith => _$UserProfileCopyWithImpl<UserProfile>(this as UserProfile, _$identity);

  /// Serializes this UserProfile to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UserProfile&&(identical(other.userId, userId) || other.userId == userId)&&(identical(other.username, username) || other.username == username)&&(identical(other.headline, headline) || other.headline == headline)&&(identical(other.bio, bio) || other.bio == bio)&&(identical(other.location, location) || other.location == location)&&(identical(other.avatarKey, avatarKey) || other.avatarKey == avatarKey)&&(identical(other.avatarUrl, avatarUrl) || other.avatarUrl == avatarUrl)&&(identical(other.isPublic, isPublic) || other.isPublic == isPublic)&&const DeepCollectionEquality().equals(other.experiences, experiences)&&const DeepCollectionEquality().equals(other.education, education)&&const DeepCollectionEquality().equals(other.projects, projects)&&const DeepCollectionEquality().equals(other.skills, skills)&&const DeepCollectionEquality().equals(other.certifications, certifications)&&const DeepCollectionEquality().equals(other.languages, languages)&&const DeepCollectionEquality().equals(other.achievements, achievements)&&const DeepCollectionEquality().equals(other.socialLinks, socialLinks));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,userId,username,headline,bio,location,avatarKey,avatarUrl,isPublic,const DeepCollectionEquality().hash(experiences),const DeepCollectionEquality().hash(education),const DeepCollectionEquality().hash(projects),const DeepCollectionEquality().hash(skills),const DeepCollectionEquality().hash(certifications),const DeepCollectionEquality().hash(languages),const DeepCollectionEquality().hash(achievements),const DeepCollectionEquality().hash(socialLinks));

@override
String toString() {
  return 'UserProfile(userId: $userId, username: $username, headline: $headline, bio: $bio, location: $location, avatarKey: $avatarKey, avatarUrl: $avatarUrl, isPublic: $isPublic, experiences: $experiences, education: $education, projects: $projects, skills: $skills, certifications: $certifications, languages: $languages, achievements: $achievements, socialLinks: $socialLinks)';
}


}

/// @nodoc
abstract mixin class $UserProfileCopyWith<$Res>  {
  factory $UserProfileCopyWith(UserProfile value, $Res Function(UserProfile) _then) = _$UserProfileCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'user_id') String userId, String? username, String? headline, String? bio, String? location,@JsonKey(name: 'avatar_key') String? avatarKey,@JsonKey(name: 'avatar_url') String? avatarUrl,@JsonKey(name: 'is_public') bool isPublic, List<UserExperience> experiences, List<UserEducation> education, List<UserProject> projects, List<UserSkill> skills, List<UserCertification> certifications, List<UserLanguage> languages, List<UserAchievement> achievements,@JsonKey(name: 'social_links') List<UserSocialLink> socialLinks
});




}
/// @nodoc
class _$UserProfileCopyWithImpl<$Res>
    implements $UserProfileCopyWith<$Res> {
  _$UserProfileCopyWithImpl(this._self, this._then);

  final UserProfile _self;
  final $Res Function(UserProfile) _then;

/// Create a copy of UserProfile
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? userId = null,Object? username = freezed,Object? headline = freezed,Object? bio = freezed,Object? location = freezed,Object? avatarKey = freezed,Object? avatarUrl = freezed,Object? isPublic = null,Object? experiences = null,Object? education = null,Object? projects = null,Object? skills = null,Object? certifications = null,Object? languages = null,Object? achievements = null,Object? socialLinks = null,}) {
  return _then(_self.copyWith(
userId: null == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String,username: freezed == username ? _self.username : username // ignore: cast_nullable_to_non_nullable
as String?,headline: freezed == headline ? _self.headline : headline // ignore: cast_nullable_to_non_nullable
as String?,bio: freezed == bio ? _self.bio : bio // ignore: cast_nullable_to_non_nullable
as String?,location: freezed == location ? _self.location : location // ignore: cast_nullable_to_non_nullable
as String?,avatarKey: freezed == avatarKey ? _self.avatarKey : avatarKey // ignore: cast_nullable_to_non_nullable
as String?,avatarUrl: freezed == avatarUrl ? _self.avatarUrl : avatarUrl // ignore: cast_nullable_to_non_nullable
as String?,isPublic: null == isPublic ? _self.isPublic : isPublic // ignore: cast_nullable_to_non_nullable
as bool,experiences: null == experiences ? _self.experiences : experiences // ignore: cast_nullable_to_non_nullable
as List<UserExperience>,education: null == education ? _self.education : education // ignore: cast_nullable_to_non_nullable
as List<UserEducation>,projects: null == projects ? _self.projects : projects // ignore: cast_nullable_to_non_nullable
as List<UserProject>,skills: null == skills ? _self.skills : skills // ignore: cast_nullable_to_non_nullable
as List<UserSkill>,certifications: null == certifications ? _self.certifications : certifications // ignore: cast_nullable_to_non_nullable
as List<UserCertification>,languages: null == languages ? _self.languages : languages // ignore: cast_nullable_to_non_nullable
as List<UserLanguage>,achievements: null == achievements ? _self.achievements : achievements // ignore: cast_nullable_to_non_nullable
as List<UserAchievement>,socialLinks: null == socialLinks ? _self.socialLinks : socialLinks // ignore: cast_nullable_to_non_nullable
as List<UserSocialLink>,
  ));
}

}


/// Adds pattern-matching-related methods to [UserProfile].
extension UserProfilePatterns on UserProfile {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _UserProfile value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _UserProfile() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _UserProfile value)  $default,){
final _that = this;
switch (_that) {
case _UserProfile():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _UserProfile value)?  $default,){
final _that = this;
switch (_that) {
case _UserProfile() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'user_id')  String userId,  String? username,  String? headline,  String? bio,  String? location, @JsonKey(name: 'avatar_key')  String? avatarKey, @JsonKey(name: 'avatar_url')  String? avatarUrl, @JsonKey(name: 'is_public')  bool isPublic,  List<UserExperience> experiences,  List<UserEducation> education,  List<UserProject> projects,  List<UserSkill> skills,  List<UserCertification> certifications,  List<UserLanguage> languages,  List<UserAchievement> achievements, @JsonKey(name: 'social_links')  List<UserSocialLink> socialLinks)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _UserProfile() when $default != null:
return $default(_that.userId,_that.username,_that.headline,_that.bio,_that.location,_that.avatarKey,_that.avatarUrl,_that.isPublic,_that.experiences,_that.education,_that.projects,_that.skills,_that.certifications,_that.languages,_that.achievements,_that.socialLinks);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'user_id')  String userId,  String? username,  String? headline,  String? bio,  String? location, @JsonKey(name: 'avatar_key')  String? avatarKey, @JsonKey(name: 'avatar_url')  String? avatarUrl, @JsonKey(name: 'is_public')  bool isPublic,  List<UserExperience> experiences,  List<UserEducation> education,  List<UserProject> projects,  List<UserSkill> skills,  List<UserCertification> certifications,  List<UserLanguage> languages,  List<UserAchievement> achievements, @JsonKey(name: 'social_links')  List<UserSocialLink> socialLinks)  $default,) {final _that = this;
switch (_that) {
case _UserProfile():
return $default(_that.userId,_that.username,_that.headline,_that.bio,_that.location,_that.avatarKey,_that.avatarUrl,_that.isPublic,_that.experiences,_that.education,_that.projects,_that.skills,_that.certifications,_that.languages,_that.achievements,_that.socialLinks);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'user_id')  String userId,  String? username,  String? headline,  String? bio,  String? location, @JsonKey(name: 'avatar_key')  String? avatarKey, @JsonKey(name: 'avatar_url')  String? avatarUrl, @JsonKey(name: 'is_public')  bool isPublic,  List<UserExperience> experiences,  List<UserEducation> education,  List<UserProject> projects,  List<UserSkill> skills,  List<UserCertification> certifications,  List<UserLanguage> languages,  List<UserAchievement> achievements, @JsonKey(name: 'social_links')  List<UserSocialLink> socialLinks)?  $default,) {final _that = this;
switch (_that) {
case _UserProfile() when $default != null:
return $default(_that.userId,_that.username,_that.headline,_that.bio,_that.location,_that.avatarKey,_that.avatarUrl,_that.isPublic,_that.experiences,_that.education,_that.projects,_that.skills,_that.certifications,_that.languages,_that.achievements,_that.socialLinks);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _UserProfile implements UserProfile {
  const _UserProfile({@JsonKey(name: 'user_id') required this.userId, this.username, this.headline, this.bio, this.location, @JsonKey(name: 'avatar_key') this.avatarKey, @JsonKey(name: 'avatar_url') this.avatarUrl, @JsonKey(name: 'is_public') this.isPublic = false, final  List<UserExperience> experiences = const [], final  List<UserEducation> education = const [], final  List<UserProject> projects = const [], final  List<UserSkill> skills = const [], final  List<UserCertification> certifications = const [], final  List<UserLanguage> languages = const [], final  List<UserAchievement> achievements = const [], @JsonKey(name: 'social_links') final  List<UserSocialLink> socialLinks = const []}): _experiences = experiences,_education = education,_projects = projects,_skills = skills,_certifications = certifications,_languages = languages,_achievements = achievements,_socialLinks = socialLinks;
  factory _UserProfile.fromJson(Map<String, dynamic> json) => _$UserProfileFromJson(json);

@override@JsonKey(name: 'user_id') final  String userId;
@override final  String? username;
@override final  String? headline;
@override final  String? bio;
@override final  String? location;
@override@JsonKey(name: 'avatar_key') final  String? avatarKey;
@override@JsonKey(name: 'avatar_url') final  String? avatarUrl;
@override@JsonKey(name: 'is_public') final  bool isPublic;
 final  List<UserExperience> _experiences;
@override@JsonKey() List<UserExperience> get experiences {
  if (_experiences is EqualUnmodifiableListView) return _experiences;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_experiences);
}

 final  List<UserEducation> _education;
@override@JsonKey() List<UserEducation> get education {
  if (_education is EqualUnmodifiableListView) return _education;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_education);
}

 final  List<UserProject> _projects;
@override@JsonKey() List<UserProject> get projects {
  if (_projects is EqualUnmodifiableListView) return _projects;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_projects);
}

 final  List<UserSkill> _skills;
@override@JsonKey() List<UserSkill> get skills {
  if (_skills is EqualUnmodifiableListView) return _skills;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_skills);
}

 final  List<UserCertification> _certifications;
@override@JsonKey() List<UserCertification> get certifications {
  if (_certifications is EqualUnmodifiableListView) return _certifications;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_certifications);
}

 final  List<UserLanguage> _languages;
@override@JsonKey() List<UserLanguage> get languages {
  if (_languages is EqualUnmodifiableListView) return _languages;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_languages);
}

 final  List<UserAchievement> _achievements;
@override@JsonKey() List<UserAchievement> get achievements {
  if (_achievements is EqualUnmodifiableListView) return _achievements;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_achievements);
}

 final  List<UserSocialLink> _socialLinks;
@override@JsonKey(name: 'social_links') List<UserSocialLink> get socialLinks {
  if (_socialLinks is EqualUnmodifiableListView) return _socialLinks;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_socialLinks);
}


/// Create a copy of UserProfile
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$UserProfileCopyWith<_UserProfile> get copyWith => __$UserProfileCopyWithImpl<_UserProfile>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$UserProfileToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _UserProfile&&(identical(other.userId, userId) || other.userId == userId)&&(identical(other.username, username) || other.username == username)&&(identical(other.headline, headline) || other.headline == headline)&&(identical(other.bio, bio) || other.bio == bio)&&(identical(other.location, location) || other.location == location)&&(identical(other.avatarKey, avatarKey) || other.avatarKey == avatarKey)&&(identical(other.avatarUrl, avatarUrl) || other.avatarUrl == avatarUrl)&&(identical(other.isPublic, isPublic) || other.isPublic == isPublic)&&const DeepCollectionEquality().equals(other._experiences, _experiences)&&const DeepCollectionEquality().equals(other._education, _education)&&const DeepCollectionEquality().equals(other._projects, _projects)&&const DeepCollectionEquality().equals(other._skills, _skills)&&const DeepCollectionEquality().equals(other._certifications, _certifications)&&const DeepCollectionEquality().equals(other._languages, _languages)&&const DeepCollectionEquality().equals(other._achievements, _achievements)&&const DeepCollectionEquality().equals(other._socialLinks, _socialLinks));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,userId,username,headline,bio,location,avatarKey,avatarUrl,isPublic,const DeepCollectionEquality().hash(_experiences),const DeepCollectionEquality().hash(_education),const DeepCollectionEquality().hash(_projects),const DeepCollectionEquality().hash(_skills),const DeepCollectionEquality().hash(_certifications),const DeepCollectionEquality().hash(_languages),const DeepCollectionEquality().hash(_achievements),const DeepCollectionEquality().hash(_socialLinks));

@override
String toString() {
  return 'UserProfile(userId: $userId, username: $username, headline: $headline, bio: $bio, location: $location, avatarKey: $avatarKey, avatarUrl: $avatarUrl, isPublic: $isPublic, experiences: $experiences, education: $education, projects: $projects, skills: $skills, certifications: $certifications, languages: $languages, achievements: $achievements, socialLinks: $socialLinks)';
}


}

/// @nodoc
abstract mixin class _$UserProfileCopyWith<$Res> implements $UserProfileCopyWith<$Res> {
  factory _$UserProfileCopyWith(_UserProfile value, $Res Function(_UserProfile) _then) = __$UserProfileCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'user_id') String userId, String? username, String? headline, String? bio, String? location,@JsonKey(name: 'avatar_key') String? avatarKey,@JsonKey(name: 'avatar_url') String? avatarUrl,@JsonKey(name: 'is_public') bool isPublic, List<UserExperience> experiences, List<UserEducation> education, List<UserProject> projects, List<UserSkill> skills, List<UserCertification> certifications, List<UserLanguage> languages, List<UserAchievement> achievements,@JsonKey(name: 'social_links') List<UserSocialLink> socialLinks
});




}
/// @nodoc
class __$UserProfileCopyWithImpl<$Res>
    implements _$UserProfileCopyWith<$Res> {
  __$UserProfileCopyWithImpl(this._self, this._then);

  final _UserProfile _self;
  final $Res Function(_UserProfile) _then;

/// Create a copy of UserProfile
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? userId = null,Object? username = freezed,Object? headline = freezed,Object? bio = freezed,Object? location = freezed,Object? avatarKey = freezed,Object? avatarUrl = freezed,Object? isPublic = null,Object? experiences = null,Object? education = null,Object? projects = null,Object? skills = null,Object? certifications = null,Object? languages = null,Object? achievements = null,Object? socialLinks = null,}) {
  return _then(_UserProfile(
userId: null == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String,username: freezed == username ? _self.username : username // ignore: cast_nullable_to_non_nullable
as String?,headline: freezed == headline ? _self.headline : headline // ignore: cast_nullable_to_non_nullable
as String?,bio: freezed == bio ? _self.bio : bio // ignore: cast_nullable_to_non_nullable
as String?,location: freezed == location ? _self.location : location // ignore: cast_nullable_to_non_nullable
as String?,avatarKey: freezed == avatarKey ? _self.avatarKey : avatarKey // ignore: cast_nullable_to_non_nullable
as String?,avatarUrl: freezed == avatarUrl ? _self.avatarUrl : avatarUrl // ignore: cast_nullable_to_non_nullable
as String?,isPublic: null == isPublic ? _self.isPublic : isPublic // ignore: cast_nullable_to_non_nullable
as bool,experiences: null == experiences ? _self._experiences : experiences // ignore: cast_nullable_to_non_nullable
as List<UserExperience>,education: null == education ? _self._education : education // ignore: cast_nullable_to_non_nullable
as List<UserEducation>,projects: null == projects ? _self._projects : projects // ignore: cast_nullable_to_non_nullable
as List<UserProject>,skills: null == skills ? _self._skills : skills // ignore: cast_nullable_to_non_nullable
as List<UserSkill>,certifications: null == certifications ? _self._certifications : certifications // ignore: cast_nullable_to_non_nullable
as List<UserCertification>,languages: null == languages ? _self._languages : languages // ignore: cast_nullable_to_non_nullable
as List<UserLanguage>,achievements: null == achievements ? _self._achievements : achievements // ignore: cast_nullable_to_non_nullable
as List<UserAchievement>,socialLinks: null == socialLinks ? _self._socialLinks : socialLinks // ignore: cast_nullable_to_non_nullable
as List<UserSocialLink>,
  ));
}


}


/// @nodoc
mixin _$ProfileUpsertRequest {

 String? get username; String? get headline; String? get bio; String? get location;@JsonKey(name: 'is_public') bool? get isPublic;
/// Create a copy of ProfileUpsertRequest
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProfileUpsertRequestCopyWith<ProfileUpsertRequest> get copyWith => _$ProfileUpsertRequestCopyWithImpl<ProfileUpsertRequest>(this as ProfileUpsertRequest, _$identity);

  /// Serializes this ProfileUpsertRequest to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProfileUpsertRequest&&(identical(other.username, username) || other.username == username)&&(identical(other.headline, headline) || other.headline == headline)&&(identical(other.bio, bio) || other.bio == bio)&&(identical(other.location, location) || other.location == location)&&(identical(other.isPublic, isPublic) || other.isPublic == isPublic));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,username,headline,bio,location,isPublic);

@override
String toString() {
  return 'ProfileUpsertRequest(username: $username, headline: $headline, bio: $bio, location: $location, isPublic: $isPublic)';
}


}

/// @nodoc
abstract mixin class $ProfileUpsertRequestCopyWith<$Res>  {
  factory $ProfileUpsertRequestCopyWith(ProfileUpsertRequest value, $Res Function(ProfileUpsertRequest) _then) = _$ProfileUpsertRequestCopyWithImpl;
@useResult
$Res call({
 String? username, String? headline, String? bio, String? location,@JsonKey(name: 'is_public') bool? isPublic
});




}
/// @nodoc
class _$ProfileUpsertRequestCopyWithImpl<$Res>
    implements $ProfileUpsertRequestCopyWith<$Res> {
  _$ProfileUpsertRequestCopyWithImpl(this._self, this._then);

  final ProfileUpsertRequest _self;
  final $Res Function(ProfileUpsertRequest) _then;

/// Create a copy of ProfileUpsertRequest
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? username = freezed,Object? headline = freezed,Object? bio = freezed,Object? location = freezed,Object? isPublic = freezed,}) {
  return _then(_self.copyWith(
username: freezed == username ? _self.username : username // ignore: cast_nullable_to_non_nullable
as String?,headline: freezed == headline ? _self.headline : headline // ignore: cast_nullable_to_non_nullable
as String?,bio: freezed == bio ? _self.bio : bio // ignore: cast_nullable_to_non_nullable
as String?,location: freezed == location ? _self.location : location // ignore: cast_nullable_to_non_nullable
as String?,isPublic: freezed == isPublic ? _self.isPublic : isPublic // ignore: cast_nullable_to_non_nullable
as bool?,
  ));
}

}


/// Adds pattern-matching-related methods to [ProfileUpsertRequest].
extension ProfileUpsertRequestPatterns on ProfileUpsertRequest {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ProfileUpsertRequest value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ProfileUpsertRequest() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ProfileUpsertRequest value)  $default,){
final _that = this;
switch (_that) {
case _ProfileUpsertRequest():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ProfileUpsertRequest value)?  $default,){
final _that = this;
switch (_that) {
case _ProfileUpsertRequest() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? username,  String? headline,  String? bio,  String? location, @JsonKey(name: 'is_public')  bool? isPublic)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ProfileUpsertRequest() when $default != null:
return $default(_that.username,_that.headline,_that.bio,_that.location,_that.isPublic);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? username,  String? headline,  String? bio,  String? location, @JsonKey(name: 'is_public')  bool? isPublic)  $default,) {final _that = this;
switch (_that) {
case _ProfileUpsertRequest():
return $default(_that.username,_that.headline,_that.bio,_that.location,_that.isPublic);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? username,  String? headline,  String? bio,  String? location, @JsonKey(name: 'is_public')  bool? isPublic)?  $default,) {final _that = this;
switch (_that) {
case _ProfileUpsertRequest() when $default != null:
return $default(_that.username,_that.headline,_that.bio,_that.location,_that.isPublic);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ProfileUpsertRequest implements ProfileUpsertRequest {
  const _ProfileUpsertRequest({this.username, this.headline, this.bio, this.location, @JsonKey(name: 'is_public') this.isPublic});
  factory _ProfileUpsertRequest.fromJson(Map<String, dynamic> json) => _$ProfileUpsertRequestFromJson(json);

@override final  String? username;
@override final  String? headline;
@override final  String? bio;
@override final  String? location;
@override@JsonKey(name: 'is_public') final  bool? isPublic;

/// Create a copy of ProfileUpsertRequest
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ProfileUpsertRequestCopyWith<_ProfileUpsertRequest> get copyWith => __$ProfileUpsertRequestCopyWithImpl<_ProfileUpsertRequest>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ProfileUpsertRequestToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ProfileUpsertRequest&&(identical(other.username, username) || other.username == username)&&(identical(other.headline, headline) || other.headline == headline)&&(identical(other.bio, bio) || other.bio == bio)&&(identical(other.location, location) || other.location == location)&&(identical(other.isPublic, isPublic) || other.isPublic == isPublic));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,username,headline,bio,location,isPublic);

@override
String toString() {
  return 'ProfileUpsertRequest(username: $username, headline: $headline, bio: $bio, location: $location, isPublic: $isPublic)';
}


}

/// @nodoc
abstract mixin class _$ProfileUpsertRequestCopyWith<$Res> implements $ProfileUpsertRequestCopyWith<$Res> {
  factory _$ProfileUpsertRequestCopyWith(_ProfileUpsertRequest value, $Res Function(_ProfileUpsertRequest) _then) = __$ProfileUpsertRequestCopyWithImpl;
@override @useResult
$Res call({
 String? username, String? headline, String? bio, String? location,@JsonKey(name: 'is_public') bool? isPublic
});




}
/// @nodoc
class __$ProfileUpsertRequestCopyWithImpl<$Res>
    implements _$ProfileUpsertRequestCopyWith<$Res> {
  __$ProfileUpsertRequestCopyWithImpl(this._self, this._then);

  final _ProfileUpsertRequest _self;
  final $Res Function(_ProfileUpsertRequest) _then;

/// Create a copy of ProfileUpsertRequest
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? username = freezed,Object? headline = freezed,Object? bio = freezed,Object? location = freezed,Object? isPublic = freezed,}) {
  return _then(_ProfileUpsertRequest(
username: freezed == username ? _self.username : username // ignore: cast_nullable_to_non_nullable
as String?,headline: freezed == headline ? _self.headline : headline // ignore: cast_nullable_to_non_nullable
as String?,bio: freezed == bio ? _self.bio : bio // ignore: cast_nullable_to_non_nullable
as String?,location: freezed == location ? _self.location : location // ignore: cast_nullable_to_non_nullable
as String?,isPublic: freezed == isPublic ? _self.isPublic : isPublic // ignore: cast_nullable_to_non_nullable
as bool?,
  ));
}


}


/// @nodoc
mixin _$MasterResume {

@JsonKey(name: 'resume_id') String get resumeId;@JsonKey(name: 'file_name') String get fileName;@JsonKey(name: 'file_path') String get filePath;
/// Create a copy of MasterResume
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MasterResumeCopyWith<MasterResume> get copyWith => _$MasterResumeCopyWithImpl<MasterResume>(this as MasterResume, _$identity);

  /// Serializes this MasterResume to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is MasterResume&&(identical(other.resumeId, resumeId) || other.resumeId == resumeId)&&(identical(other.fileName, fileName) || other.fileName == fileName)&&(identical(other.filePath, filePath) || other.filePath == filePath));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,resumeId,fileName,filePath);

@override
String toString() {
  return 'MasterResume(resumeId: $resumeId, fileName: $fileName, filePath: $filePath)';
}


}

/// @nodoc
abstract mixin class $MasterResumeCopyWith<$Res>  {
  factory $MasterResumeCopyWith(MasterResume value, $Res Function(MasterResume) _then) = _$MasterResumeCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'resume_id') String resumeId,@JsonKey(name: 'file_name') String fileName,@JsonKey(name: 'file_path') String filePath
});




}
/// @nodoc
class _$MasterResumeCopyWithImpl<$Res>
    implements $MasterResumeCopyWith<$Res> {
  _$MasterResumeCopyWithImpl(this._self, this._then);

  final MasterResume _self;
  final $Res Function(MasterResume) _then;

/// Create a copy of MasterResume
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? resumeId = null,Object? fileName = null,Object? filePath = null,}) {
  return _then(_self.copyWith(
resumeId: null == resumeId ? _self.resumeId : resumeId // ignore: cast_nullable_to_non_nullable
as String,fileName: null == fileName ? _self.fileName : fileName // ignore: cast_nullable_to_non_nullable
as String,filePath: null == filePath ? _self.filePath : filePath // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [MasterResume].
extension MasterResumePatterns on MasterResume {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _MasterResume value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _MasterResume() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _MasterResume value)  $default,){
final _that = this;
switch (_that) {
case _MasterResume():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _MasterResume value)?  $default,){
final _that = this;
switch (_that) {
case _MasterResume() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'resume_id')  String resumeId, @JsonKey(name: 'file_name')  String fileName, @JsonKey(name: 'file_path')  String filePath)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MasterResume() when $default != null:
return $default(_that.resumeId,_that.fileName,_that.filePath);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'resume_id')  String resumeId, @JsonKey(name: 'file_name')  String fileName, @JsonKey(name: 'file_path')  String filePath)  $default,) {final _that = this;
switch (_that) {
case _MasterResume():
return $default(_that.resumeId,_that.fileName,_that.filePath);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'resume_id')  String resumeId, @JsonKey(name: 'file_name')  String fileName, @JsonKey(name: 'file_path')  String filePath)?  $default,) {final _that = this;
switch (_that) {
case _MasterResume() when $default != null:
return $default(_that.resumeId,_that.fileName,_that.filePath);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _MasterResume implements MasterResume {
  const _MasterResume({@JsonKey(name: 'resume_id') required this.resumeId, @JsonKey(name: 'file_name') required this.fileName, @JsonKey(name: 'file_path') required this.filePath});
  factory _MasterResume.fromJson(Map<String, dynamic> json) => _$MasterResumeFromJson(json);

@override@JsonKey(name: 'resume_id') final  String resumeId;
@override@JsonKey(name: 'file_name') final  String fileName;
@override@JsonKey(name: 'file_path') final  String filePath;

/// Create a copy of MasterResume
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MasterResumeCopyWith<_MasterResume> get copyWith => __$MasterResumeCopyWithImpl<_MasterResume>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MasterResumeToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _MasterResume&&(identical(other.resumeId, resumeId) || other.resumeId == resumeId)&&(identical(other.fileName, fileName) || other.fileName == fileName)&&(identical(other.filePath, filePath) || other.filePath == filePath));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,resumeId,fileName,filePath);

@override
String toString() {
  return 'MasterResume(resumeId: $resumeId, fileName: $fileName, filePath: $filePath)';
}


}

/// @nodoc
abstract mixin class _$MasterResumeCopyWith<$Res> implements $MasterResumeCopyWith<$Res> {
  factory _$MasterResumeCopyWith(_MasterResume value, $Res Function(_MasterResume) _then) = __$MasterResumeCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'resume_id') String resumeId,@JsonKey(name: 'file_name') String fileName,@JsonKey(name: 'file_path') String filePath
});




}
/// @nodoc
class __$MasterResumeCopyWithImpl<$Res>
    implements _$MasterResumeCopyWith<$Res> {
  __$MasterResumeCopyWithImpl(this._self, this._then);

  final _MasterResume _self;
  final $Res Function(_MasterResume) _then;

/// Create a copy of MasterResume
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? resumeId = null,Object? fileName = null,Object? filePath = null,}) {
  return _then(_MasterResume(
resumeId: null == resumeId ? _self.resumeId : resumeId // ignore: cast_nullable_to_non_nullable
as String,fileName: null == fileName ? _self.fileName : fileName // ignore: cast_nullable_to_non_nullable
as String,filePath: null == filePath ? _self.filePath : filePath // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on

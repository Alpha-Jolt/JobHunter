import 'package:flutter/material.dart';
import 'app_badge.dart';

/// Application status pill mapping backend enum values.
enum ApplicationStatus { sent, replied, interviewScheduled, rejected, ghosted }

class ApplicationStatusPill extends StatelessWidget {
  const ApplicationStatusPill({required this.status, super.key});

  final ApplicationStatus status;

  String get _label {
    switch (status) {
      case ApplicationStatus.sent:
        return 'Sent';
      case ApplicationStatus.replied:
        return 'Replied';
      case ApplicationStatus.interviewScheduled:
        return 'Interview';
      case ApplicationStatus.rejected:
        return 'Rejected';
      case ApplicationStatus.ghosted:
        return 'No response';
    }
  }

  AppBadgeVariant get _variant {
    switch (status) {
      case ApplicationStatus.sent:
        return AppBadgeVariant.info;
      case ApplicationStatus.replied:
        return AppBadgeVariant.success;
      case ApplicationStatus.interviewScheduled:
        return AppBadgeVariant.success;
      case ApplicationStatus.rejected:
        return AppBadgeVariant.error;
      case ApplicationStatus.ghosted:
        return AppBadgeVariant.neutral;
    }
  }

  @override
  Widget build(BuildContext context) {
    return AppBadge(label: _label, variant: _variant);
  }
}

/// Parses raw application status string from API.
ApplicationStatus parseApplicationStatus(String? raw) {
  switch (raw) {
    case 'replied':
      return ApplicationStatus.replied;
    case 'interview_scheduled':
      return ApplicationStatus.interviewScheduled;
    case 'rejected':
      return ApplicationStatus.rejected;
    case 'ghosted':
      return ApplicationStatus.ghosted;
    default:
      return ApplicationStatus.sent;
  }
}

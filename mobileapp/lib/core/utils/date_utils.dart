import 'package:intl/intl.dart';

/// Date/time formatting utilities used across the app.
abstract class DateUtils {
  static String formatShort(DateTime? dt) {
    if (dt == null) return '';
    return DateFormat('d MMM yyyy').format(dt.toLocal());
  }

  static String formatRelative(DateTime? dt) {
    if (dt == null) return '';
    final now = DateTime.now();
    final diff = now.difference(dt.toLocal());
    if (diff.inMinutes < 1) return 'just now';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    if (diff.inDays < 7) return '${diff.inDays}d ago';
    return formatShort(dt);
  }

  static String formatMonthYear(DateTime? dt) {
    if (dt == null) return '';
    return DateFormat('MMM yyyy').format(dt.toLocal());
  }

  /// Returns hours remaining until [expiryTime]. Negative if already expired.
  static int hoursUntil(DateTime expiryTime) {
    return expiryTime.difference(DateTime.now()).inHours;
  }

  static DateTime? tryParse(String? value) {
    if (value == null || value.isEmpty) return null;
    return DateTime.tryParse(value);
  }
}

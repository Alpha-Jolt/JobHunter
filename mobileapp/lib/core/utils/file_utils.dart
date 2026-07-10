import 'dart:typed_data';
import 'package:mime/mime.dart';

/// Client-side file validation utilities.
/// Server-side validation is always the authoritative check.
/// These are pre-flight guards to give immediate feedback.
abstract class FileUtils {
  // ── Resume validation (PDF / DOCX, max 10 MB) ─────────────────────────────

  static const int _resumeMaxBytes = 10 * 1024 * 1024;
  static const List<String> _resumeExtensions = ['.pdf', '.docx'];

  static String? validateResume(String fileName, int fileSize, Uint8List bytes) {
    final ext = _extension(fileName);
    if (!_resumeExtensions.contains(ext)) {
      return 'Only PDF and DOCX files are supported.';
    }
    if (fileSize > _resumeMaxBytes) {
      return 'File must be smaller than 10 MB.';
    }
    if (ext == '.pdf' && !_isPdf(bytes)) {
      return 'File does not appear to be a valid PDF.';
    }
    if (ext == '.docx' && !_isDocx(bytes)) {
      return 'File does not appear to be a valid DOCX.';
    }
    return null; // valid
  }

  // ── Avatar validation (JPEG / PNG / WEBP, max 5 MB) ──────────────────────

  static const int _avatarMaxBytes = 5 * 1024 * 1024;
  static const List<String> _avatarExtensions = ['.jpg', '.jpeg', '.png', '.webp'];

  static String? validateAvatar(String fileName, int fileSize, Uint8List bytes) {
    final ext = _extension(fileName);
    if (!_avatarExtensions.contains(ext)) {
      return 'Only JPEG, PNG, and WEBP images are supported.';
    }
    if (fileSize > _avatarMaxBytes) {
      return 'Image must be smaller than 5 MB.';
    }
    final mime = lookupMimeType(fileName, headerBytes: bytes);
    if (mime == null ||
        !['image/jpeg', 'image/png', 'image/webp'].contains(mime)) {
      return 'Invalid image format.';
    }
    return null; // valid
  }

  // ── Magic byte checks ─────────────────────────────────────────────────────

  static bool _isPdf(Uint8List bytes) {
    if (bytes.length < 4) return false;
    // PDF magic: %PDF
    return bytes[0] == 0x25 &&
        bytes[1] == 0x50 &&
        bytes[2] == 0x44 &&
        bytes[3] == 0x46;
  }

  static bool _isDocx(Uint8List bytes) {
    if (bytes.length < 4) return false;
    // DOCX (ZIP) magic: PK\x03\x04
    return bytes[0] == 0x50 &&
        bytes[1] == 0x4B &&
        bytes[2] == 0x03 &&
        bytes[3] == 0x04;
  }

  // ── Helpers ───────────────────────────────────────────────────────────────

  static String _extension(String fileName) {
    final dot = fileName.lastIndexOf('.');
    if (dot == -1) return '';
    return fileName.substring(dot).toLowerCase();
  }
}

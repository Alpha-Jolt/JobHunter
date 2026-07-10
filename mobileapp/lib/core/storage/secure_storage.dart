import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Wrapper around [FlutterSecureStorage] with typed read/write helpers.
///
/// Only non-sensitive preference data (theme, telemetry consent) is stored
/// here as well — but access tokens are NEVER written to this store.
class SecureStorage {
  SecureStorage() : _storage = const FlutterSecureStorage(
        aOptions: AndroidOptions(),
        iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
      );

  final FlutterSecureStorage _storage;

  static const String _keyRefreshToken = 'jh_refresh_token';
  static const String _keyTelemetryConsent = 'jh_telemetry_consent';
  static const String _keyThemeMode = 'jh_theme_mode';

  // ── Refresh token ──────────────────────────────────────────────────────────

  Future<void> saveRefreshToken(String token) =>
      _storage.write(key: _keyRefreshToken, value: token);

  Future<String?> getRefreshToken() =>
      _storage.read(key: _keyRefreshToken);

  Future<void> deleteRefreshToken() =>
      _storage.delete(key: _keyRefreshToken);

  // ── Telemetry consent ──────────────────────────────────────────────────────

  Future<void> saveTelemetryConsent({required bool granted}) =>
      _storage.write(key: _keyTelemetryConsent, value: granted.toString());

  Future<bool?> getTelemetryConsent() async {
    final value = await _storage.read(key: _keyTelemetryConsent);
    if (value == null) return null;
    return value == 'true';
  }

  // ── Theme preference ───────────────────────────────────────────────────────

  Future<void> saveThemeMode(String mode) =>
      _storage.write(key: _keyThemeMode, value: mode);

  Future<String?> getThemeMode() =>
      _storage.read(key: _keyThemeMode);

  // ── Full clear (on logout) ─────────────────────────────────────────────────

  Future<void> clearAll() => _storage.deleteAll();
}

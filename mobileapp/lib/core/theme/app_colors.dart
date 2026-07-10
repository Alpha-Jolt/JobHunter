import 'package:flutter/material.dart';

/// Brand and semantic color tokens sourced from webapp/src/app/globals.css.
abstract class AppColors {
  // Brand
  static const Color brandOrange = Color(0xFFF97316);
  static const Color brandOrangeDark = Color(0xFFEA580C);
  static const Color brandCharcoal = Color(0xFF3D3D3D);

  // Light mode
  static const Color backgroundLight = Color(0xFFFFFFFF);
  static const Color backgroundSubtleLight = Color(0xFFF9FAFB);
  static const Color foregroundLight = Color(0xFF111827);
  static const Color foregroundMutedLight = Color(0xFF6B7280);
  static const Color borderLight = Color(0xFFE5E7EB);
  static const Color cardLight = Color(0xFFFFFFFF);
  static const Color inputBorderLight = Color(0xFFD1D5DB);
  static const Color secondaryLight = Color(0xFFF3F4F6);
  static const Color secondaryForegroundLight = Color(0xFF374151);
  static const Color mutedLight = Color(0xFFF3F4F6);
  static const Color mutedForegroundLight = Color(0xFF6B7280);
  static const Color accentLight = Color(0xFFFFF7ED);
  static const Color accentForegroundLight = Color(0xFFEA580C);

  // Dark mode
  static const Color backgroundDark = Color(0xFF111827);
  static const Color backgroundSubtleDark = Color(0xFF1F2937);
  static const Color foregroundDark = Color(0xFFF9FAFB);
  static const Color foregroundMutedDark = Color(0xFF9CA3AF);
  static const Color borderDark = Color(0xFF374151);
  static const Color cardDark = Color(0xFF1F2937);
  static const Color inputBorderDark = Color(0xFF4B5563);
  static const Color secondaryDark = Color(0xFF374151);
  static const Color secondaryForegroundDark = Color(0xFFF3F4F6);
  static const Color mutedDark = Color(0xFF374151);
  static const Color mutedForegroundDark = Color(0xFF9CA3AF);
  static const Color accentDark = Color(0xFF431407);
  static const Color accentForegroundDark = Color(0xFFFB923C);

  // Semantic (theme-independent)
  static const Color destructive = Color(0xFFEF4444);
  static const Color destructiveForeground = Color(0xFFFFFFFF);
  static const Color primary = brandOrange;
  static const Color primaryForeground = Color(0xFFFFFFFF);

  // Status colors
  static const Color successGreen = Color(0xFF22C55E);
  static const Color warningAmber = Color(0xFFF59E0B);
  static const Color infoBlue = Color(0xFF3B82F6);
}

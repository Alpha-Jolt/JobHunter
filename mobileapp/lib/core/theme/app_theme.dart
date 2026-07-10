import 'package:flutter/material.dart';
import 'app_colors.dart';
import 'app_spacing.dart';
import 'app_typography.dart';

/// Light and dark ThemeData built from brand tokens.
abstract class AppTheme {
  static ThemeData get light => _buildTheme(
        brightness: Brightness.light,
        background: AppColors.backgroundLight,
        backgroundSubtle: AppColors.backgroundSubtleLight,
        foreground: AppColors.foregroundLight,
        foregroundMuted: AppColors.foregroundMutedLight,
        border: AppColors.borderLight,
        card: AppColors.cardLight,
        inputBorder: AppColors.inputBorderLight,
        textTheme: AppTypography.lightTextTheme,
      );

  static ThemeData get dark => _buildTheme(
        brightness: Brightness.dark,
        background: AppColors.backgroundDark,
        backgroundSubtle: AppColors.backgroundSubtleDark,
        foreground: AppColors.foregroundDark,
        foregroundMuted: AppColors.foregroundMutedDark,
        border: AppColors.borderDark,
        card: AppColors.cardDark,
        inputBorder: AppColors.inputBorderDark,
        textTheme: AppTypography.darkTextTheme,
      );

  static ThemeData _buildTheme({
    required Brightness brightness,
    required Color background,
    required Color backgroundSubtle,
    required Color foreground,
    required Color foregroundMuted,
    required Color border,
    required Color card,
    required Color inputBorder,
    required TextTheme textTheme,
  }) {
    return ThemeData(
      useMaterial3: true,
      brightness: brightness,
      colorScheme: ColorScheme(
        brightness: brightness,
        primary: AppColors.primary,
        onPrimary: AppColors.primaryForeground,
        secondary: brightness == Brightness.light
            ? AppColors.secondaryLight
            : AppColors.secondaryDark,
        onSecondary: brightness == Brightness.light
            ? AppColors.secondaryForegroundLight
            : AppColors.secondaryForegroundDark,
        error: AppColors.destructive,
        onError: AppColors.destructiveForeground,
        surface: card,
        onSurface: foreground,
      ),
      scaffoldBackgroundColor: background,
      cardColor: card,
      dividerColor: border,
      textTheme: textTheme,
      appBarTheme: AppBarTheme(
        backgroundColor: background,
        foregroundColor: foreground,
        elevation: 0,
        surfaceTintColor: Colors.transparent,
        titleTextStyle: textTheme.titleLarge,
      ),
      cardTheme: CardThemeData(
        color: card,
        elevation: 1,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadius.lg),
          side: BorderSide(color: border, width: 1),
        ),
        margin: EdgeInsets.zero,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: background,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.lg,
          vertical: AppSpacing.md,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.md),
          borderSide: BorderSide(color: inputBorder),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.md),
          borderSide: BorderSide(color: inputBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.md),
          borderSide: const BorderSide(color: AppColors.primary, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.md),
          borderSide: const BorderSide(color: AppColors.destructive),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.md),
          borderSide: const BorderSide(color: AppColors.destructive, width: 2),
        ),
        hintStyle: TextStyle(color: foregroundMuted),
        labelStyle: TextStyle(color: foregroundMuted),
        errorStyle: const TextStyle(color: AppColors.destructive, fontSize: 12),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary,
          foregroundColor: AppColors.primaryForeground,
          elevation: 0,
          padding: const EdgeInsets.symmetric(
            horizontal: AppSpacing.xl2,
            vertical: AppSpacing.md,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppRadius.md),
          ),
          textStyle: textTheme.labelLarge,
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: AppColors.primary,
          side: const BorderSide(color: AppColors.primary),
          padding: const EdgeInsets.symmetric(
            horizontal: AppSpacing.xl2,
            vertical: AppSpacing.md,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppRadius.md),
          ),
          textStyle: textTheme.labelLarge,
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: AppColors.primary,
          textStyle: textTheme.labelLarge,
        ),
      ),
      bottomNavigationBarTheme: BottomNavigationBarThemeData(
        backgroundColor: card,
        selectedItemColor: AppColors.primary,
        unselectedItemColor: foregroundMuted,
        type: BottomNavigationBarType.fixed,
        elevation: 8,
      ),
      snackBarTheme: SnackBarThemeData(
        backgroundColor: foreground,
        contentTextStyle: TextStyle(color: background),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadius.md),
        ),
      ),
      bottomSheetTheme: BottomSheetThemeData(
        backgroundColor: card,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(
            top: Radius.circular(AppRadius.xl),
          ),
        ),
      ),
      chipTheme: ChipThemeData(
        backgroundColor: backgroundSubtle,
        labelStyle: textTheme.bodySmall,
        side: BorderSide(color: border),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadius.full),
        ),
        padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.sm,
          vertical: AppSpacing.xs,
        ),
      ),
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: AppColors.primary,
      ),
    );
  }
}

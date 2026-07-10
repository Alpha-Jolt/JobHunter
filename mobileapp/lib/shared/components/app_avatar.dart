import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';

/// Circular avatar — shows network image with initials fallback.
class AppAvatar extends StatelessWidget {
  const AppAvatar({
    this.imageUrl,
    this.initials,
    this.radius = 20,
    super.key,
  });

  final String? imageUrl;
  final String? initials;
  final double radius;

  @override
  Widget build(BuildContext context) {
    if (imageUrl != null && imageUrl!.isNotEmpty) {
      return CircleAvatar(
        radius: radius,
        backgroundColor: AppColors.primary.withValues(alpha: 0.1),
        child: ClipOval(
          child: CachedNetworkImage(
            imageUrl: imageUrl!,
            width: radius * 2,
            height: radius * 2,
            fit: BoxFit.cover,
            placeholder: (_, __) => _Initials(
              initials: initials,
              radius: radius,
            ),
            errorWidget: (_, __, ___) => _Initials(
              initials: initials,
              radius: radius,
            ),
          ),
        ),
      );
    }
    return _Initials(initials: initials, radius: radius);
  }
}

class _Initials extends StatelessWidget {
  const _Initials({this.initials, required this.radius});

  final String? initials;
  final double radius;

  @override
  Widget build(BuildContext context) {
    return CircleAvatar(
      radius: radius,
      backgroundColor: AppColors.primary.withValues(alpha: 0.15),
      child: Text(
        (initials ?? '?').toUpperCase().characters.take(2).string,
        style: TextStyle(
          color: AppColors.primary,
          fontSize: radius * 0.65,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}

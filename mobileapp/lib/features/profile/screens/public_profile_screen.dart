import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../shared/components/app_avatar.dart';
import '../../../shared/components/app_skeleton.dart';
import '../../../shared/components/error_banner.dart';
import '../providers/profile_provider.dart';

/// Displays a user's public profile by username.
/// Accessible without authentication.
class PublicProfileScreen extends ConsumerWidget {
  const PublicProfileScreen({required this.username, super.key});

  final String username;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileAsync = ref.watch(publicProfileProvider(username));
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: Text('@$username')),
      body: profileAsync.when(
        loading: () => const _PublicProfileSkeleton(),
        error: (e, _) => Center(
          child: ErrorBanner(
            message: e.toString(),
            onRetry: () => ref.invalidate(publicProfileProvider(username)),
          ),
        ),
        data: (profile) => ListView(
          padding: const EdgeInsets.all(AppSpacing.lg),
          children: [
            Center(
              child: AppAvatar(
                imageUrl: profile.avatarUrl,
                initials: profile.username ?? username,
                radius: 40,
              ),
            ),
            const SizedBox(height: AppSpacing.md),
            if (profile.headline != null)
              Center(
                child: Text(
                  profile.headline!,
                  style: theme.textTheme.titleMedium,
                  textAlign: TextAlign.center,
                ),
              ),
            if (profile.bio != null) ...[
              const SizedBox(height: AppSpacing.lg),
              Text(profile.bio!, style: theme.textTheme.bodyMedium),
            ],
            if (profile.skills.isNotEmpty) ...[
              const SizedBox(height: AppSpacing.xl2),
              Text('Skills', style: theme.textTheme.titleSmall),
              const SizedBox(height: AppSpacing.sm),
              Wrap(
                spacing: AppSpacing.sm,
                runSpacing: AppSpacing.sm,
                children: profile.skills
                    .map((s) => Chip(label: Text(s.name)))
                    .toList(),
              ),
            ],
            if (profile.experiences.isNotEmpty) ...[
              const SizedBox(height: AppSpacing.xl2),
              Text('Experience', style: theme.textTheme.titleSmall),
              const SizedBox(height: AppSpacing.sm),
              ...profile.experiences.map(
                (e) => ListTile(
                  contentPadding: EdgeInsets.zero,
                  title: Text(e.jobTitle),
                  subtitle: Text('${e.company} · ${e.location}'),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _PublicProfileSkeleton extends StatelessWidget {
  const _PublicProfileSkeleton();

  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.all(AppSpacing.lg),
      child: Column(
        children: [
          Center(child: AppSkeleton(width: 80, height: 80, borderRadius: 40)),
          SizedBox(height: AppSpacing.md),
          AppSkeleton(width: 160, height: 20),
          SizedBox(height: AppSpacing.xl2),
          AppSkeleton(height: 60),
          SizedBox(height: AppSpacing.sm),
          AppSkeleton(height: 60),
        ],
      ),
    );
  }
}

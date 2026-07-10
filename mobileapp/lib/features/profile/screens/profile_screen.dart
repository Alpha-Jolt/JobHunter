import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../shared/components/app_avatar.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/components/app_divider.dart';
import '../../../shared/components/empty_state.dart';
import '../../../shared/components/error_banner.dart';
import '../../../shared/components/app_skeleton.dart';
import '../../../shared/components/profile_section.dart';
import '../../auth/providers/session_provider.dart';
import '../providers/profile_provider.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileAsync = ref.watch(profileProvider);
    final session = ref.watch(sessionProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            tooltip: 'Settings',
            onPressed: () => _showSettingsMenu(context, ref),
          ),
        ],
      ),
      body: profileAsync.when(
        loading: () => const _ProfileSkeleton(),
        error: (e, _) => Center(
          child: ErrorBanner(
            message: e.toString(),
            onRetry: () => ref.invalidate(profileProvider),
          ),
        ),
        data: (profile) => RefreshIndicator(
          onRefresh: () =>
              ref.read(profileProvider.notifier).refresh(),
          child: ListView(
            padding: const EdgeInsets.only(bottom: AppSpacing.xl4),
            children: [
              // Header card
              _ProfileHeader(
                displayName:
                    '${session.user?.firstName ?? ''} ${session.user?.lastName ?? ''}'
                        .trim(),
                email: session.user?.email ?? '',
                headline: profile.headline,
                avatarUrl: profile.avatarUrl,
                username: profile.username,
                onEditTap: () => context.push('/profile/edit'),
                onAvatarTap: () => _onAvatarAction(context, ref),
              ),
              const SizedBox(height: AppSpacing.sm),

              // Resume section
              _ResumeTile(
                onUpload: () => context.push('/profile/resume'),
              ),
              const SizedBox(height: AppSpacing.sm),

              // Bio
              if (profile.bio != null)
                ProfileSection(
                  title: 'About',
                  child: Text(profile.bio!,
                      style: Theme.of(context).textTheme.bodyMedium),
                ),

              // Skills
              if (profile.skills.isNotEmpty)
                ProfileSection(
                  title: 'Skills',
                  child: Wrap(
                    spacing: AppSpacing.sm,
                    runSpacing: AppSpacing.sm,
                    children: profile.skills
                        .map((s) => Chip(label: Text(s.name)))
                        .toList(),
                  ),
                ),

              // Experience
              if (profile.experiences.isNotEmpty)
                ProfileSection(
                  title: 'Experience',
                  child: Column(
                    children: profile.experiences
                        .map((e) => _ExperienceTile(exp: e))
                        .toList(),
                  ),
                ),

              // Education
              if (profile.education.isNotEmpty)
                ProfileSection(
                  title: 'Education',
                  child: Column(
                    children: profile.education
                        .map((e) => _EducationTile(edu: e))
                        .toList(),
                  ),
                ),

              // Social links
              if (profile.socialLinks.isNotEmpty)
                ProfileSection(
                  title: 'Links',
                  child: Column(
                    children: profile.socialLinks
                        .map(
                          (l) => Padding(
                            padding: const EdgeInsets.only(
                                bottom: AppSpacing.xs),
                            child: Row(
                              children: [
                                const Icon(Icons.link_outlined, size: 16),
                                const SizedBox(width: AppSpacing.sm),
                                Text(
                                  l.platform,
                                  style: Theme.of(context)
                                      .textTheme
                                      .bodySmall
                                      ?.copyWith(
                                        color: Theme.of(context)
                                            .colorScheme
                                            .primary,
                                      ),
                                ),
                              ],
                            ),
                          ),
                        )
                        .toList(),
                  ),
                ),

              if (profile.skills.isEmpty &&
                  profile.experiences.isEmpty &&
                  profile.education.isEmpty)
                EmptyState(
                  title: 'Your profile is empty.',
                  subtitle: 'Add your experience and skills to get started.',
                  actionLabel: 'Edit Profile',
                  onAction: () => context.push('/profile/edit'),
                ),
            ],
          ),
        ),
      ),
    );
  }

  void _showSettingsMenu(BuildContext context, WidgetRef ref) {
    showModalBottomSheet<void>(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (_) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.lock_outline),
              title: const Text('Change Password'),
              onTap: () {
                Navigator.of(context).pop();
                context.push('/profile/password');
              },
            ),
            ListTile(
              leading: const Icon(Icons.person_outline),
              title: const Text('View Public Profile'),
              onTap: () {
                Navigator.of(context).pop();
                final profile =
                    ref.read(profileProvider).when(data: (d) => d, error: (_, _) => null, loading: () => null);
                if (profile?.username != null) {
                  context.push('/u/${profile!.username}');
                }
              },
            ),
            const AppDivider(),
            ListTile(
              leading: const Icon(Icons.logout, color: Colors.red),
              title: const Text('Logout',
                  style: TextStyle(color: Colors.red)),
              onTap: () {
                Navigator.of(context).pop();
                _confirmLogout(context, ref);
              },
            ),
          ],
        ),
      ),
    );
  }

  void _confirmLogout(BuildContext context, WidgetRef ref) {
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Logout'),
        content: const Text('Are you sure you want to logout?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Cancel'),
          ),
          TextButton(
            style:
                TextButton.styleFrom(foregroundColor: Colors.red),
            onPressed: () async {
              Navigator.of(ctx).pop();
              await ref.read(sessionProvider.notifier).logout();
            },
            child: const Text('Logout'),
          ),
        ],
      ),
    );
  }

  void _onAvatarAction(BuildContext context, WidgetRef ref) {
    // Avatar edit actions surfaced in EditProfileScreen — navigate there.
    context.push('/profile/edit');
  }
}

// ── Profile header ────────────────────────────────────────────────────────────

class _ProfileHeader extends StatelessWidget {
  const _ProfileHeader({
    required this.displayName,
    required this.email,
    this.headline,
    this.avatarUrl,
    this.username,
    required this.onEditTap,
    required this.onAvatarTap,
  });

  final String displayName;
  final String email;
  final String? headline;
  final String? avatarUrl;
  final String? username;
  final VoidCallback onEditTap;
  final VoidCallback onAvatarTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.all(AppSpacing.xl2),
      color: theme.colorScheme.surface,
      child: Column(
        children: [
          GestureDetector(
            onTap: onAvatarTap,
            child: AppAvatar(
              imageUrl: avatarUrl,
              initials: displayName,
              radius: 40,
            ),
          ),
          const SizedBox(height: AppSpacing.md),
          Text(
            displayName.isNotEmpty ? displayName : email,
            style: theme.textTheme.titleLarge,
          ),
          if (headline != null) ...[
            const SizedBox(height: AppSpacing.xs),
            Text(
              headline!,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
              textAlign: TextAlign.center,
            ),
          ],
          if (username != null) ...[
            const SizedBox(height: AppSpacing.xs),
            Text(
              '@$username',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.primary,
              ),
            ),
          ],
          const SizedBox(height: AppSpacing.lg),
          AppButton(
            label: 'Edit Profile',
            onPressed: onEditTap,
            variant: AppButtonVariant.outlined,
            icon: Icons.edit_outlined,
            fullWidth: false,
          ),
        ],
      ),
    );
  }
}

// ── Resume tile ───────────────────────────────────────────────────────────────

class _ResumeTile extends StatelessWidget {
  const _ResumeTile({required this.onUpload});
  final VoidCallback onUpload;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      tileColor: Theme.of(context).colorScheme.surface,
      leading: const Icon(Icons.description_outlined),
      title: const Text('Master Resume'),
      subtitle: const Text('Upload or update your base resume'),
      trailing: const Icon(Icons.chevron_right),
      onTap: onUpload,
    );
  }
}

// ── Experience tile ───────────────────────────────────────────────────────────

class _ExperienceTile extends StatelessWidget {
  const _ExperienceTile({required this.exp});
  final dynamic exp;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(exp.jobTitle as String,
              style: theme.textTheme.titleSmall
                  ?.copyWith(fontWeight: FontWeight.w600)),
          Text('${exp.company} · ${exp.location}',
              style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant)),
          Text(
            '${exp.startDate}'
            '${exp.isCurrent == true ? ' – Present' : exp.endDate != null ? ' – ${exp.endDate}' : ''}',
            style: theme.textTheme.bodySmall
                ?.copyWith(color: theme.colorScheme.onSurfaceVariant),
          ),
        ],
      ),
    );
  }
}

// ── Education tile ────────────────────────────────────────────────────────────

class _EducationTile extends StatelessWidget {
  const _EducationTile({required this.edu});
  final dynamic edu;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(edu.institution as String,
              style: theme.textTheme.titleSmall
                  ?.copyWith(fontWeight: FontWeight.w600)),
          Text(
            '${edu.degree}'
            '${edu.fieldOfStudy != null ? ' · ${edu.fieldOfStudy}' : ''}',
            style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant),
          ),
          Text(
            '${edu.startYear}'
            '${edu.isCurrent == true ? ' – Present' : edu.endYear != null ? ' – ${edu.endYear}' : ''}',
            style: theme.textTheme.bodySmall
                ?.copyWith(color: theme.colorScheme.onSurfaceVariant),
          ),
        ],
      ),
    );
  }
}

// ── Loading skeleton ──────────────────────────────────────────────────────────

class _ProfileSkeleton extends StatelessWidget {
  const _ProfileSkeleton();

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      children: [
        const Center(
          child: AppSkeleton(width: 80, height: 80, borderRadius: 40),
        ),
        const SizedBox(height: AppSpacing.md),
        const Center(
          child: AppSkeleton(width: 160, height: 20),
        ),
        const SizedBox(height: AppSpacing.xl2),
        for (var i = 0; i < 4; i++) ...[
          const AppSkeleton(height: 80),
          const SizedBox(height: AppSpacing.sm),
        ],
      ],
    );
  }
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/components/app_text_field.dart';
import '../../../shared/components/error_banner.dart';
import '../../../shared/components/loading_overlay.dart';
import '../data/profile_models.dart';
import '../providers/profile_provider.dart';
import 'profile_sub_resources.dart';

/// Full profile edit screen.
/// - Top section: basic fields (username, headline, bio, location, visibility)
/// - Bottom sections: sub-resource CRUD for Experience, Education, Projects
class EditProfileScreen extends ConsumerStatefulWidget {
  const EditProfileScreen({super.key});

  @override
  ConsumerState<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends ConsumerState<EditProfileScreen> {
  final _formKey = GlobalKey<FormState>();

  late TextEditingController _usernameCtrl;
  late TextEditingController _headlineCtrl;
  late TextEditingController _bioCtrl;
  late TextEditingController _locationCtrl;
  bool _isPublic = false;

  bool _isLoading = false;
  String? _errorMessage;
  bool _initialized = false;

  @override
  void initState() {
    super.initState();
    _usernameCtrl = TextEditingController();
    _headlineCtrl = TextEditingController();
    _bioCtrl = TextEditingController();
    _locationCtrl = TextEditingController();
  }

  @override
  void dispose() {
    _usernameCtrl.dispose();
    _headlineCtrl.dispose();
    _bioCtrl.dispose();
    _locationCtrl.dispose();
    super.dispose();
  }

  void _initFromProfile(UserProfile profile) {
    if (_initialized) return;
    _initialized = true;
    _usernameCtrl.text = profile.username ?? '';
    _headlineCtrl.text = profile.headline ?? '';
    _bioCtrl.text = profile.bio ?? '';
    _locationCtrl.text = profile.location ?? '';
    _isPublic = profile.isPublic;
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });
    try {
      await ref.read(profileProvider.notifier).upsert(
            ProfileUpsertRequest(
              username: _usernameCtrl.text.trim().isEmpty
                  ? null
                  : _usernameCtrl.text.trim(),
              headline: _headlineCtrl.text.trim().isEmpty
                  ? null
                  : _headlineCtrl.text.trim(),
              bio: _bioCtrl.text.trim().isEmpty
                  ? null
                  : _bioCtrl.text.trim(),
              location: _locationCtrl.text.trim().isEmpty
                  ? null
                  : _locationCtrl.text.trim(),
              isPublic: _isPublic,
            ),
          );
      if (mounted) context.pop();
    } catch (e) {
      setState(() => _errorMessage = e.toString());
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final profileAsync = ref.watch(profileProvider);

    return profileAsync.when(
      loading: () =>
          const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (e, _) => Scaffold(
        appBar: AppBar(title: const Text('Edit Profile')),
        body: Center(
          child: ErrorBanner(
            message: e.toString(),
            onRetry: () => ref.invalidate(profileProvider),
          ),
        ),
      ),
      data: (profile) {
        _initFromProfile(profile);
        return LoadingOverlay(
          isLoading: _isLoading,
          child: Scaffold(
            appBar: AppBar(
              title: const Text('Edit Profile'),
              actions: [
                TextButton(
                  onPressed: _isLoading ? null : _save,
                  child: const Text('Save'),
                ),
              ],
            ),
            body: Form(
              key: _formKey,
              child: ListView(
                padding: const EdgeInsets.all(AppSpacing.lg),
                children: [
                  if (_errorMessage != null) ...[
                    ErrorBanner(message: _errorMessage!),
                    const SizedBox(height: AppSpacing.lg),
                  ],
                  // ── Basic fields ──────────────────────────────────────────
                  AppTextField(
                    controller: _usernameCtrl,
                    label: 'Username',
                    hint: 'your_username',
                    keyboardType: TextInputType.text,
                  ),
                  const SizedBox(height: AppSpacing.lg),
                  AppTextField(
                    controller: _headlineCtrl,
                    label: 'Headline',
                    hint: 'Software Engineer · Open to Work',
                    keyboardType: TextInputType.text,
                  ),
                  const SizedBox(height: AppSpacing.lg),
                  AppTextField(
                    controller: _bioCtrl,
                    label: 'Bio',
                    hint: 'A short description about yourself',
                    keyboardType: TextInputType.multiline,
                    maxLines: 4,
                  ),
                  const SizedBox(height: AppSpacing.lg),
                  AppTextField(
                    controller: _locationCtrl,
                    label: 'Location',
                    hint: 'Bangalore, India',
                    keyboardType: TextInputType.text,
                  ),
                  const SizedBox(height: AppSpacing.lg),
                  SwitchListTile(
                    title: const Text('Public Profile'),
                    subtitle: const Text(
                        'Allow others to view your profile via your username link'),
                    value: _isPublic,
                    onChanged: (v) => setState(() => _isPublic = v),
                  ),
                  const SizedBox(height: AppSpacing.xl3),
                  AppButton(
                    label: 'Save Changes',
                    onPressed: _isLoading ? null : _save,
                    isLoading: _isLoading,
                  ),
                  const SizedBox(height: AppSpacing.xl3),
                  // ── Sub-resource sections ─────────────────────────────────
                  ExperienceSection(profile: profile),
                  const SizedBox(height: AppSpacing.xl2),
                  EducationSection(profile: profile),
                  const SizedBox(height: AppSpacing.xl2),
                  ProjectsSection(profile: profile),
                  const SizedBox(height: AppSpacing.xl4),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}

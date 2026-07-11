import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/components/app_text_field.dart';
import '../../../shared/components/error_banner.dart';
import '../data/profile_models.dart';
import '../providers/profile_provider.dart';

// ─────────────────────────────────────────────────────────────────────────────
// Shared helpers
// ─────────────────────────────────────────────────────────────────────────────

/// Header row used by all sub-resource sections.
class _SectionHeader extends StatelessWidget {
  const _SectionHeader({required this.title, required this.onAdd});
  final String title;
  final VoidCallback onAdd;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(title, style: Theme.of(context).textTheme.titleMedium),
        const Spacer(),
        TextButton.icon(
          onPressed: onAdd,
          icon: const Icon(Icons.add, size: 18),
          label: const Text('Add'),
        ),
      ],
    );
  }
}

/// Tile for a single sub-resource item with edit and delete actions.
class _ItemTile extends StatelessWidget {
  const _ItemTile({
    required this.title,
    required this.subtitle,
    required this.onEdit,
    required this.onDelete,
  });
  final String title;
  final String subtitle;
  final VoidCallback onEdit;
  final VoidCallback onDelete;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: AppSpacing.sm),
      child: ListTile(
        title: Text(title, style: Theme.of(context).textTheme.titleSmall),
        subtitle: Text(subtitle,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                )),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              icon: const Icon(Icons.edit_outlined, size: 18),
              onPressed: onEdit,
              tooltip: 'Edit',
            ),
            IconButton(
              icon: const Icon(Icons.delete_outline, size: 18, color: Colors.red),
              onPressed: onDelete,
              tooltip: 'Delete',
            ),
          ],
        ),
      ),
    );
  }
}

/// Shows a delete confirmation dialog. Returns true if confirmed.
Future<bool> _confirmDelete(BuildContext context, String item) async {
  final result = await showDialog<bool>(
    context: context,
    builder: (ctx) => AlertDialog(
      title: const Text('Delete'),
      content: Text('Remove "$item"?'),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(ctx).pop(false),
          child: const Text('Cancel'),
        ),
        TextButton(
          style: TextButton.styleFrom(foregroundColor: Colors.red),
          onPressed: () => Navigator.of(ctx).pop(true),
          child: const Text('Delete'),
        ),
      ],
    ),
  );
  return result ?? false;
}

// ─────────────────────────────────────────────────────────────────────────────
// Experience section
// ─────────────────────────────────────────────────────────────────────────────

class ExperienceSection extends ConsumerWidget {
  const ExperienceSection({required this.profile, super.key});
  final UserProfile profile;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _SectionHeader(
          title: 'Experience',
          onAdd: () => _openSheet(context, ref, null),
        ),
        ...profile.experiences.map(
          (e) => _ItemTile(
            title: '${e.jobTitle} · ${e.company}',
            subtitle: '${e.startDate} – ${e.isCurrent ? 'Present' : (e.endDate ?? '')}',
            onEdit: () => _openSheet(context, ref, e),
            onDelete: () async {
              if (await _confirmDelete(context, e.jobTitle)) {
                await ref
                    .read(profileRepositoryProvider)
                    .deleteExperience(e.expId!);
                ref.invalidate(profileProvider);
              }
            },
          ),
        ),
      ],
    );
  }

  void _openSheet(BuildContext context, WidgetRef ref, UserExperience? existing) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) => _ExperienceSheet(existing: existing, ref: ref),
    );
  }
}

class _ExperienceSheet extends StatefulWidget {
  const _ExperienceSheet({this.existing, required this.ref});
  final UserExperience? existing;
  final WidgetRef ref;

  @override
  State<_ExperienceSheet> createState() => _ExperienceSheetState();
}

class _ExperienceSheetState extends State<_ExperienceSheet> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _titleCtrl;
  late final TextEditingController _companyCtrl;
  late final TextEditingController _locationCtrl;
  late final TextEditingController _startCtrl;
  late final TextEditingController _endCtrl;
  late final TextEditingController _descCtrl;
  bool _isCurrent = false;
  bool _saving = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    final e = widget.existing;
    _titleCtrl = TextEditingController(text: e?.jobTitle ?? '');
    _companyCtrl = TextEditingController(text: e?.company ?? '');
    _locationCtrl = TextEditingController(text: e?.location ?? '');
    _startCtrl = TextEditingController(text: e?.startDate ?? '');
    _endCtrl = TextEditingController(text: e?.endDate ?? '');
    _descCtrl = TextEditingController(text: e?.description ?? '');
    _isCurrent = e?.isCurrent ?? false;
  }

  @override
  void dispose() {
    _titleCtrl.dispose();
    _companyCtrl.dispose();
    _locationCtrl.dispose();
    _startCtrl.dispose();
    _endCtrl.dispose();
    _descCtrl.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() { _saving = true; _error = null; });
    final repo = widget.ref.read(profileRepositoryProvider);
    final exp = UserExperience(
      expId: widget.existing?.expId,
      jobTitle: _titleCtrl.text.trim(),
      company: _companyCtrl.text.trim(),
      location: _locationCtrl.text.trim(),
      startDate: _startCtrl.text.trim(),
      endDate: _isCurrent ? null : (_endCtrl.text.trim().isEmpty ? null : _endCtrl.text.trim()),
      isCurrent: _isCurrent,
      description: _descCtrl.text.trim().isEmpty ? null : _descCtrl.text.trim(),
    );
    try {
      if (widget.existing?.expId != null) {
        await repo.updateExperience(widget.existing!.expId!, exp);
      } else {
        await repo.addExperience(exp);
      }
      widget.ref.invalidate(profileProvider);
      if (mounted) Navigator.of(context).pop();
    } catch (e) {
      setState(() { _error = e.toString(); _saving = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(bottom: MediaQuery.of(context).viewInsets.bottom),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSpacing.xl2),
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                widget.existing == null ? 'Add Experience' : 'Edit Experience',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: AppSpacing.lg),
              if (_error != null) ...[
                ErrorBanner(message: _error!),
                const SizedBox(height: AppSpacing.md),
              ],
              AppTextField(controller: _titleCtrl, label: 'Job Title', hint: 'Software Engineer',
                  validator: (v) => (v == null || v.trim().isEmpty) ? 'Required' : null),
              const SizedBox(height: AppSpacing.md),
              AppTextField(controller: _companyCtrl, label: 'Company', hint: 'Acme Corp',
                  validator: (v) => (v == null || v.trim().isEmpty) ? 'Required' : null),
              const SizedBox(height: AppSpacing.md),
              AppTextField(controller: _locationCtrl, label: 'Location', hint: 'Bangalore, India',
                  validator: (v) => (v == null || v.trim().isEmpty) ? 'Required' : null),
              const SizedBox(height: AppSpacing.md),
              AppTextField(controller: _startCtrl, label: 'Start Date', hint: 'Jan 2022',
                  validator: (v) => (v == null || v.trim().isEmpty) ? 'Required' : null),
              const SizedBox(height: AppSpacing.sm),
              CheckboxListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Currently working here'),
                value: _isCurrent,
                onChanged: (v) => setState(() => _isCurrent = v ?? false),
              ),
              if (!_isCurrent) ...[
                const SizedBox(height: AppSpacing.sm),
                AppTextField(controller: _endCtrl, label: 'End Date', hint: 'Dec 2023'),
              ],
              const SizedBox(height: AppSpacing.md),
              AppTextField(controller: _descCtrl, label: 'Description (optional)',
                  hint: 'Describe your role and achievements', maxLines: 3,
                  keyboardType: TextInputType.multiline),
              const SizedBox(height: AppSpacing.xl2),
              AppButton(label: 'Save', onPressed: _saving ? null : _save, isLoading: _saving),
              const SizedBox(height: AppSpacing.sm),
              AppButton(label: 'Cancel', onPressed: () => Navigator.of(context).pop(),
                  variant: AppButtonVariant.text),
            ],
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Education section
// ─────────────────────────────────────────────────────────────────────────────

class EducationSection extends ConsumerWidget {
  const EducationSection({required this.profile, super.key});
  final UserProfile profile;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _SectionHeader(
          title: 'Education',
          onAdd: () => _openSheet(context, ref, null),
        ),
        ...profile.education.map(
          (e) => _ItemTile(
            title: '${e.degree} · ${e.institution}',
            subtitle: '${e.startYear} – ${e.isCurrent ? 'Present' : (e.endYear?.toString() ?? '')}',
            onEdit: () => _openSheet(context, ref, e),
            onDelete: () async {
              if (await _confirmDelete(context, e.institution)) {
                await ref.read(profileRepositoryProvider).deleteEducation(e.eduId!);
                ref.invalidate(profileProvider);
              }
            },
          ),
        ),
      ],
    );
  }

  void _openSheet(BuildContext context, WidgetRef ref, UserEducation? existing) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) => _EducationSheet(existing: existing, ref: ref),
    );
  }
}

class _EducationSheet extends StatefulWidget {
  const _EducationSheet({this.existing, required this.ref});
  final UserEducation? existing;
  final WidgetRef ref;

  @override
  State<_EducationSheet> createState() => _EducationSheetState();
}

class _EducationSheetState extends State<_EducationSheet> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _instCtrl;
  late final TextEditingController _degreeCtrl;
  late final TextEditingController _fieldCtrl;
  late final TextEditingController _startCtrl;
  late final TextEditingController _endCtrl;
  bool _isCurrent = false;
  bool _saving = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    final e = widget.existing;
    _instCtrl = TextEditingController(text: e?.institution ?? '');
    _degreeCtrl = TextEditingController(text: e?.degree ?? '');
    _fieldCtrl = TextEditingController(text: e?.fieldOfStudy ?? '');
    _startCtrl = TextEditingController(text: e?.startYear.toString() ?? '');
    _endCtrl = TextEditingController(text: e?.endYear?.toString() ?? '');
    _isCurrent = e?.isCurrent ?? false;
  }

  @override
  void dispose() {
    _instCtrl.dispose();
    _degreeCtrl.dispose();
    _fieldCtrl.dispose();
    _startCtrl.dispose();
    _endCtrl.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() { _saving = true; _error = null; });
    final repo = widget.ref.read(profileRepositoryProvider);
    final startYear = int.tryParse(_startCtrl.text.trim()) ?? 0;
    final endYear = int.tryParse(_endCtrl.text.trim());
    final edu = UserEducation(
      eduId: widget.existing?.eduId,
      institution: _instCtrl.text.trim(),
      degree: _degreeCtrl.text.trim(),
      fieldOfStudy: _fieldCtrl.text.trim().isEmpty ? null : _fieldCtrl.text.trim(),
      startYear: startYear,
      endYear: _isCurrent ? null : endYear,
      isCurrent: _isCurrent,
    );
    try {
      if (widget.existing?.eduId != null) {
        await repo.updateEducation(widget.existing!.eduId!, edu);
      } else {
        await repo.addEducation(edu);
      }
      widget.ref.invalidate(profileProvider);
      if (mounted) Navigator.of(context).pop();
    } catch (e) {
      setState(() { _error = e.toString(); _saving = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(bottom: MediaQuery.of(context).viewInsets.bottom),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSpacing.xl2),
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                widget.existing == null ? 'Add Education' : 'Edit Education',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: AppSpacing.lg),
              if (_error != null) ...[
                ErrorBanner(message: _error!),
                const SizedBox(height: AppSpacing.md),
              ],
              AppTextField(controller: _instCtrl, label: 'Institution', hint: 'IIT Bombay',
                  validator: (v) => (v == null || v.trim().isEmpty) ? 'Required' : null),
              const SizedBox(height: AppSpacing.md),
              AppTextField(controller: _degreeCtrl, label: 'Degree', hint: 'B.Tech',
                  validator: (v) => (v == null || v.trim().isEmpty) ? 'Required' : null),
              const SizedBox(height: AppSpacing.md),
              AppTextField(controller: _fieldCtrl, label: 'Field of Study (optional)',
                  hint: 'Computer Science'),
              const SizedBox(height: AppSpacing.md),
              AppTextField(controller: _startCtrl, label: 'Start Year', hint: '2019',
                  keyboardType: TextInputType.number,
                  validator: (v) {
                    if (v == null || v.trim().isEmpty) return 'Required';
                    if (int.tryParse(v.trim()) == null) return 'Enter a valid year';
                    return null;
                  }),
              const SizedBox(height: AppSpacing.sm),
              CheckboxListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Currently studying here'),
                value: _isCurrent,
                onChanged: (v) => setState(() => _isCurrent = v ?? false),
              ),
              if (!_isCurrent) ...[
                const SizedBox(height: AppSpacing.sm),
                AppTextField(controller: _endCtrl, label: 'End Year', hint: '2023',
                    keyboardType: TextInputType.number),
              ],
              const SizedBox(height: AppSpacing.xl2),
              AppButton(label: 'Save', onPressed: _saving ? null : _save, isLoading: _saving),
              const SizedBox(height: AppSpacing.sm),
              AppButton(label: 'Cancel', onPressed: () => Navigator.of(context).pop(),
                  variant: AppButtonVariant.text),
            ],
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Projects section
// ─────────────────────────────────────────────────────────────────────────────

class ProjectsSection extends ConsumerWidget {
  const ProjectsSection({required this.profile, super.key});
  final UserProfile profile;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _SectionHeader(
          title: 'Projects',
          onAdd: () => _openSheet(context, ref, null),
        ),
        ...profile.projects.map(
          (p) => _ItemTile(
            title: p.name,
            subtitle: p.techStack.isNotEmpty ? p.techStack.join(', ') : 'No tech stack listed',
            onEdit: () => _openSheet(context, ref, p),
            onDelete: () async {
              if (await _confirmDelete(context, p.name)) {
                await ref.read(profileRepositoryProvider).deleteProject(p.projId!);
                ref.invalidate(profileProvider);
              }
            },
          ),
        ),
      ],
    );
  }

  void _openSheet(BuildContext context, WidgetRef ref, UserProject? existing) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) => _ProjectSheet(existing: existing, ref: ref),
    );
  }
}

class _ProjectSheet extends StatefulWidget {
  const _ProjectSheet({this.existing, required this.ref});
  final UserProject? existing;
  final WidgetRef ref;

  @override
  State<_ProjectSheet> createState() => _ProjectSheetState();
}

class _ProjectSheetState extends State<_ProjectSheet> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _nameCtrl;
  late final TextEditingController _descCtrl;
  late final TextEditingController _techCtrl;
  late final TextEditingController _urlCtrl;
  bool _saving = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    final p = widget.existing;
    _nameCtrl = TextEditingController(text: p?.name ?? '');
    _descCtrl = TextEditingController(text: p?.description ?? '');
    _techCtrl = TextEditingController(text: p?.techStack.join(', ') ?? '');
    _urlCtrl = TextEditingController(text: p?.projectUrl ?? '');
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _descCtrl.dispose();
    _techCtrl.dispose();
    _urlCtrl.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() { _saving = true; _error = null; });
    final repo = widget.ref.read(profileRepositoryProvider);
    final techStack = _techCtrl.text.trim().isEmpty
        ? <String>[]
        : _techCtrl.text.split(',').map((s) => s.trim()).where((s) => s.isNotEmpty).toList();
    final project = UserProject(
      projId: widget.existing?.projId,
      name: _nameCtrl.text.trim(),
      description: _descCtrl.text.trim().isEmpty ? null : _descCtrl.text.trim(),
      techStack: techStack,
      projectUrl: _urlCtrl.text.trim().isEmpty ? null : _urlCtrl.text.trim(),
    );
    try {
      if (widget.existing?.projId != null) {
        await repo.updateProject(widget.existing!.projId!, project);
      } else {
        await repo.addProject(project);
      }
      widget.ref.invalidate(profileProvider);
      if (mounted) Navigator.of(context).pop();
    } catch (e) {
      setState(() { _error = e.toString(); _saving = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(bottom: MediaQuery.of(context).viewInsets.bottom),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSpacing.xl2),
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                widget.existing == null ? 'Add Project' : 'Edit Project',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: AppSpacing.lg),
              if (_error != null) ...[
                ErrorBanner(message: _error!),
                const SizedBox(height: AppSpacing.md),
              ],
              AppTextField(controller: _nameCtrl, label: 'Project Name', hint: 'JobHunter App',
                  validator: (v) => (v == null || v.trim().isEmpty) ? 'Required' : null),
              const SizedBox(height: AppSpacing.md),
              AppTextField(controller: _descCtrl, label: 'Description (optional)',
                  hint: 'What this project does', maxLines: 3,
                  keyboardType: TextInputType.multiline),
              const SizedBox(height: AppSpacing.md),
              AppTextField(controller: _techCtrl, label: 'Tech Stack (comma separated)',
                  hint: 'Flutter, Dart, Python'),
              const SizedBox(height: AppSpacing.md),
              AppTextField(controller: _urlCtrl, label: 'Project URL (optional)',
                  hint: 'https://github.com/you/project',
                  keyboardType: TextInputType.url),
              const SizedBox(height: AppSpacing.xl2),
              AppButton(label: 'Save', onPressed: _saving ? null : _save, isLoading: _saving),
              const SizedBox(height: AppSpacing.sm),
              AppButton(label: 'Cancel', onPressed: () => Navigator.of(context).pop(),
                  variant: AppButtonVariant.text),
            ],
          ),
        ),
      ),
    );
  }
}

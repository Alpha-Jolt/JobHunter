import 'package:flutter/material.dart';
import 'app_badge.dart';

/// Displays the email_trust level of a job contact.
/// Low-trust contacts surface a visible warning — never silently accepted.
class EmailTrustBadge extends StatelessWidget {
  const EmailTrustBadge({required this.trust, super.key});

  final String? trust;

  @override
  Widget build(BuildContext context) {
    switch (trust) {
      case 'verified':
        return const AppBadge(
          label: 'Verified',
          variant: AppBadgeVariant.success,
          compact: true,
        );
      case 'low':
        return const AppBadge(
          label: 'Low Trust',
          variant: AppBadgeVariant.warning,
          compact: true,
        );
      default:
        return const AppBadge(
          label: 'Unverified',
          variant: AppBadgeVariant.neutral,
          compact: true,
        );
    }
  }
}

/// Warning text shown in JobDetailScreen for low-trust contacts.
/// Never silent — user must see the risk before proceeding.
class LowTrustWarning extends StatelessWidget {
  const LowTrustWarning({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFFF59E0B).withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: const Color(0xFFF59E0B).withValues(alpha: 0.3),
        ),
      ),
      child: Row(
        children: [
          const Icon(Icons.warning_amber_outlined,
              size: 18, color: Color(0xFFF59E0B)),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              'HR email appears to be a free webmail address. '
              'Proceed with awareness.',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: const Color(0xFFB45309),
                  ),
            ),
          ),
        ],
      ),
    );
  }
}

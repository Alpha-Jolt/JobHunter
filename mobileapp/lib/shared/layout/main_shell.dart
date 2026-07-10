import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../components/error_boundary.dart';

/// Persistent bottom navigation shell wrapping all 5 main tabs.
/// Each tab's content is isolated inside an [ErrorBoundaryWidget] so an
/// unhandled exception in one tab cannot crash the others.
class MainShell extends ConsumerWidget {
  const MainShell({required this.child, super.key});

  final Widget child;

  static const List<_TabItem> _tabs = [
    _TabItem(label: 'Home', icon: Icons.home_outlined, activeIcon: Icons.home, path: '/home'),
    _TabItem(label: 'Jobs', icon: Icons.work_outline, activeIcon: Icons.work, path: '/jobs'),
    _TabItem(label: 'Variants', icon: Icons.description_outlined, activeIcon: Icons.description, path: '/variants'),
    _TabItem(label: 'Applications', icon: Icons.send_outlined, activeIcon: Icons.send, path: '/applications'),
    _TabItem(label: 'Profile', icon: Icons.person_outline, activeIcon: Icons.person, path: '/profile'),
  ];

  int _locationToIndex(String location) {
    if (location.startsWith('/jobs')) return 1;
    if (location.startsWith('/variants')) return 2;
    if (location.startsWith('/applications')) return 3;
    if (location.startsWith('/profile')) return 4;
    return 0;
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final location = GoRouterState.of(context).uri.path;
    final currentIndex = _locationToIndex(location);
    final currentTab = _tabs[currentIndex];

    return Scaffold(
      // Wrap the active tab content in an ErrorBoundaryWidget.
      // If the tab throws an unhandled exception the boundary shows its
      // recovery UI while all other tabs remain fully functional.
      body: ErrorBoundaryWidget(
        key: ValueKey(currentTab.path),
        tabLabel: currentTab.label,
        child: child,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: currentIndex,
        onTap: (index) {
          if (index == currentIndex) return;
          context.go(_tabs[index].path);
        },
        items: _tabs
            .map(
              (tab) => BottomNavigationBarItem(
                icon: Icon(tab.icon),
                activeIcon: Icon(tab.activeIcon),
                label: tab.label,
              ),
            )
            .toList(),
      ),
    );
  }
}

class _TabItem {
  const _TabItem({
    required this.label,
    required this.icon,
    required this.activeIcon,
    required this.path,
  });

  final String label;
  final IconData icon;
  final IconData activeIcon;
  final String path;
}

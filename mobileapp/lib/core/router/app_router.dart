import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../features/auth/providers/session_provider.dart';
import '../../features/auth/screens/splash_screen.dart';
import '../../features/auth/screens/login_screen.dart';
import '../../features/auth/screens/signup_screen.dart';
import '../../features/dashboard/screens/home_screen.dart';
import '../../features/jobs/screens/job_list_screen.dart';
import '../../features/jobs/screens/job_detail_screen.dart';
import '../../features/variants/screens/variant_list_screen.dart';
import '../../features/variants/screens/variant_detail_screen.dart';
import '../../features/variants/screens/variant_generation_screen.dart';
import '../../features/applications/screens/application_list_screen.dart';
import '../../features/applications/screens/application_detail_screen.dart';
import '../../features/profile/screens/profile_screen.dart';
import '../../features/profile/screens/edit_profile_screen.dart';
import '../../features/profile/screens/public_profile_screen.dart';
import '../../features/profile/screens/change_password_screen.dart';
import '../../features/resume/screens/resume_upload_screen.dart';
import '../../shared/layout/main_shell.dart';
import 'route_names.dart';

part 'app_router.g.dart';

final _rootNavigatorKey = GlobalKey<NavigatorState>(debugLabel: 'root');
final _shellNavigatorKey = GlobalKey<NavigatorState>(debugLabel: 'shell');

@Riverpod(keepAlive: true)
GoRouter appRouter(Ref ref) {
  final sessionState = ref.watch(sessionProvider);

  return GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/splash',
    debugLogDiagnostics: false,
    redirect: (context, state) {
      final isLoading = sessionState.isLoading;
      final isAuthenticated = sessionState.isAuthenticated;
      final path = state.uri.path;

      if (isLoading) {
        return path == '/splash' ? null : '/splash';
      }

      final isAuthRoute = path.startsWith('/login') ||
          path.startsWith('/signup') ||
          path == '/splash';

      if (!isAuthenticated && !isAuthRoute) return '/login';
      if (isAuthenticated && isAuthRoute) return '/home';

      return null;
    },
    routes: [
      // ── Auth routes ────────────────────────────────────────────────────────
      GoRoute(
        path: '/splash',
        name: RouteNames.splash,
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/login',
        name: RouteNames.login,
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/signup',
        name: RouteNames.signup,
        builder: (context, state) => const SignupScreen(),
      ),

      // ── Public profile (no auth needed) ───────────────────────────────────
      GoRoute(
        path: '/u/:username',
        name: RouteNames.publicProfile,
        builder: (context, state) => PublicProfileScreen(
          username: state.pathParameters['username']!,
        ),
      ),

      // ── Main shell (tabs) ─────────────────────────────────────────────────
      ShellRoute(
        navigatorKey: _shellNavigatorKey,
        builder: (context, state, child) => MainShell(child: child),
        routes: [
          // Tab 0 — Home
          GoRoute(
            path: '/home',
            name: RouteNames.home,
            builder: (context, state) => const HomeScreen(),
          ),

          // Tab 1 — Jobs
          GoRoute(
            path: '/jobs',
            name: RouteNames.jobs,
            builder: (context, state) => const JobListScreen(),
            routes: [
              GoRoute(
                path: ':jobId',
                name: RouteNames.jobDetail,
                builder: (context, state) => JobDetailScreen(
                  jobId: state.pathParameters['jobId']!,
                ),
                routes: [
                  GoRoute(
                    path: 'generate',
                    name: RouteNames.variantGeneration,
                    builder: (context, state) => VariantGenerationScreen(
                      jobId: state.pathParameters['jobId']!,
                    ),
                  ),
                ],
              ),
            ],
          ),

          // Tab 2 — Variants
          GoRoute(
            path: '/variants',
            name: RouteNames.variants,
            builder: (context, state) => const VariantListScreen(),
            routes: [
              GoRoute(
                path: ':variantId',
                name: RouteNames.variantDetail,
                builder: (context, state) => VariantDetailScreen(
                  variantId: state.pathParameters['variantId']!,
                ),
              ),
            ],
          ),

          // Tab 3 — Applications
          GoRoute(
            path: '/applications',
            name: RouteNames.applications,
            builder: (context, state) => const ApplicationListScreen(),
            routes: [
              GoRoute(
                path: ':applicationId',
                name: RouteNames.applicationDetail,
                builder: (context, state) => ApplicationDetailScreen(
                  applicationId: state.pathParameters['applicationId']!,
                ),
              ),
            ],
          ),

          // Tab 4 — Profile
          GoRoute(
            path: '/profile',
            name: RouteNames.profile,
            builder: (context, state) => const ProfileScreen(),
            routes: [
              GoRoute(
                path: 'edit',
                name: RouteNames.editProfile,
                builder: (context, state) => const EditProfileScreen(),
              ),
              GoRoute(
                path: 'resume',
                name: RouteNames.resumeUpload,
                builder: (context, state) => const ResumeUploadScreen(),
              ),
              GoRoute(
                path: 'password',
                name: RouteNames.changePassword,
                builder: (context, state) => const ChangePasswordScreen(),
              ),
            ],
          ),
        ],
      ),
    ],
    errorBuilder: (context, state) => Scaffold(
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline, size: 48),
            const SizedBox(height: 16),
            const Text('Page not found'),
            TextButton(
              onPressed: () => context.go('/home'),
              child: const Text('Go Home'),
            ),
          ],
        ),
      ),
    ),
  );
}

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../features/auth/presentation/screens/login_screen.dart';
import '../../features/auth/presentation/screens/register_screen.dart';
import '../../features/auth/presentation/screens/forgot_password_screen.dart';
import '../../features/dashboard/presentation/screens/dashboard_screen.dart';
import '../../features/dashboard/presentation/screens/shell_screen.dart';
import '../../features/clients/presentation/screens/clients_list_screen.dart';
import '../../features/clients/presentation/screens/client_detail_screen.dart';
import '../../features/messages/presentation/screens/messages_screen.dart';
import '../../features/profile/presentation/screens/profile_screen.dart';
import '../../features/programs/presentation/screens/programs_list_screen.dart';
import '../../features/programs/presentation/screens/create_program_screen.dart';
import '../../features/programs/presentation/screens/program_detail_screen.dart';
import '../../features/tracking/presentation/screens/client_program_screen.dart';
import '../../features/tracking/presentation/screens/metrics_screen.dart';
import '../../features/tracking/presentation/screens/progression_dashboard_screen.dart';
import '../../features/auth/presentation/screens/splash_screen.dart';

final _rootNavigatorKey = GlobalKey<NavigatorState>();

final appRouter = GoRouter(
  navigatorKey: _rootNavigatorKey,
  initialLocation: '/splash',
  routes: [
    GoRoute(path: '/splash', builder: (_, __) => const SplashScreen()),
    GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
    GoRoute(path: '/register', builder: (_, __) => const RegisterScreen()),
    GoRoute(path: '/forgot-password', builder: (_, __) => const ForgotPasswordScreen()),
    StatefulShellRoute.indexedStack(
      builder: (_, __, navigationShell) =>
          ShellScreen(navigationShell: navigationShell),
      branches: [
        StatefulShellBranch(routes: [
          GoRoute(path: '/dashboard', builder: (_, __) => const DashboardScreen()),
        ]),
        StatefulShellBranch(routes: [
          GoRoute(
            path: '/clients',
            builder: (_, __) => const ClientsListScreen(),
            routes: [
              GoRoute(
                path: ':id',
                builder: (_, state) =>
                    ClientDetailScreen(clientId: state.pathParameters['id']!),
              ),
            ],
          ),
        ]),
        StatefulShellBranch(routes: [
          GoRoute(
            path: '/programs',
            builder: (_, __) => const ProgramsListScreen(),
            routes: [
              GoRoute(path: 'create', builder: (_, __) => const CreateProgramScreen()),
              GoRoute(
                path: ':id',
                builder: (_, state) =>
                    ProgramDetailScreen(programId: state.pathParameters['id']!),
              ),
            ],
          ),
        ]),
        StatefulShellBranch(routes: [
          GoRoute(path: '/messages', builder: (_, __) => const MessagesScreen()),
        ]),
        StatefulShellBranch(routes: [
          GoRoute(path: '/profile', builder: (_, __) => const ProfileScreen()),
        ]),
      ],
    ),
    GoRoute(
      path: '/tracking/program/:id',
      builder: (_, state) =>
          ClientProgramScreen(programId: state.pathParameters['id']!),
    ),
    GoRoute(path: '/tracking/metrics', builder: (_, __) => const MetricsScreen()),
    GoRoute(path: '/tracking/progression', builder: (_, __) => const ProgressionDashboardScreen()),
  ],
);

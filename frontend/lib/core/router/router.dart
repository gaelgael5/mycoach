import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/login',
    routes: [
      GoRoute(path: '/login', builder: (ctx, state) => const Placeholder()),
      GoRoute(path: '/register', builder: (ctx, state) => const Placeholder()),
      GoRoute(path: '/home', builder: (ctx, state) => const Placeholder()),
      GoRoute(path: '/coach/dashboard', builder: (ctx, state) => const Placeholder()),
      // deep link enrollment
      GoRoute(
        path: '/enroll/:token',
        builder: (ctx, state) => const Placeholder(
          // state.pathParameters['token']
        ),
      ),
    ],
  );
});

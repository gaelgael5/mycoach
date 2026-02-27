import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'core/router/router.dart';
import 'core/theme/app_theme.dart';
// Généré par `flutter gen-l10n` (ne pas éditer manuellement)
// ignore: depend_on_referenced_packages
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(
    const ProviderScope(
      child: MyCoachApp(),
    ),
  );
}

class MyCoachApp extends ConsumerWidget {
  const MyCoachApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      title: 'MyCoach',
      // Thème dark en priorité — app dark-first.
      theme:      AppTheme.light,
      darkTheme:  AppTheme.dark,
      themeMode:  ThemeMode.dark,
      routerConfig: router,
      // i18n
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: AppLocalizations.supportedLocales,
      // Résolution locale : préférence stockée > locale système > fr par défaut.
      localeResolutionCallback: (locale, supported) {
        if (locale == null) return const Locale('fr');
        for (final s in supported) {
          if (s.languageCode == locale.languageCode) return s;
        }
        return const Locale('fr');
      },
      debugShowCheckedModeBanner: false,
    );
  }
}

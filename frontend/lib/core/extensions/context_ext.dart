import 'package:flutter/material.dart';
// ignore: depend_on_referenced_packages
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

/// Extension pratique pour accéder aux traductions depuis n'importe quel contexte.
/// Usage : `context.l10n.loginTitle`
extension AppLocalizationsX on BuildContext {
  AppLocalizations get l10n => AppLocalizations.of(this);
}

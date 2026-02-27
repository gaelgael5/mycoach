import 'package:equatable/equatable.dart';

/// Plateformes standard supportées.
const List<String> kValidPlatforms = [
  'instagram', 'tiktok', 'youtube', 'linkedin',
  'x', 'facebook', 'strava', 'website',
];

/// Visibilité d'un lien social.
enum LinkVisibility {
  public,
  coachesOnly;

  static LinkVisibility fromString(String s) => s == 'coaches_only'
      ? LinkVisibility.coachesOnly
      : LinkVisibility.public;

  String get value => this == LinkVisibility.coachesOnly ? 'coaches_only' : 'public';
}

/// Lien réseau social d'un utilisateur (coach ou client).
class SocialLink extends Equatable {
  const SocialLink({
    required this.id,
    this.platform,       // null = lien custom
    required this.url,
    this.label,
    this.position = 0,
    this.visibility = LinkVisibility.public,
  });

  final String id;

  /// Slug plateforme (`'instagram'`, `'youtube'`…) ou `null` pour les liens custom.
  final String? platform;

  final String url;

  /// Libellé affiché (obligatoire si platform = null).
  final String? label;

  final int position;
  final LinkVisibility visibility;

  bool get isCustom => platform == null;

  String get displayLabel => label ?? platform ?? 'Lien';

  factory SocialLink.fromJson(Map<String, dynamic> json) => SocialLink(
    id:         json['id'] as String,
    platform:   json['platform'] as String?,
    url:        json['url'] as String,
    label:      json['label'] as String?,
    position:   json['position'] as int? ?? 0,
    visibility: LinkVisibility.fromString(
      json['visibility'] as String? ?? 'public',
    ),
  );

  Map<String, dynamic> toJson() => {
    'id':         id,
    if (platform != null) 'platform': platform,
    'url':        url,
    if (label != null)    'label':    label,
    'position':   position,
    'visibility': visibility.value,
  };

  @override
  List<Object?> get props => [id, platform, url, label, position, visibility];
}

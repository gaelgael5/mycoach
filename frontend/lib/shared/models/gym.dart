import 'package:equatable/equatable.dart';

/// Une salle de sport du répertoire MyCoach.
class Gym extends Equatable {
  const Gym({
    required this.id,
    required this.name,
    required this.brand,
    required this.address,
    required this.city,
    required this.postalCode,
    required this.country,
    this.coachesCount = 0,
    this.isFavorite = false,
    this.latitude,
    this.longitude,
  });

  final String id;
  final String name;
  final String brand;     // slug ex: 'fitness_park', 'basic_fit'
  final String address;
  final String city;
  final String postalCode;
  final String country;   // ISO 3166-1 alpha-2
  final int coachesCount;
  final bool isFavorite;
  final double? latitude;
  final double? longitude;

  /// Adresse formatée courte pour l'affichage.
  String get shortAddress => '$address, $postalCode $city';

  /// Label de l'enseigne humanisé.
  String get brandLabel => switch (brand) {
    'fitness_park'   => 'Fitness Park',
    'basic_fit'      => 'Basic-Fit',
    'cmg'            => 'CMG Sports Club',
    'neoness'        => 'Neoness',
    'keep_cool'      => 'Keep Cool',
    'orange_bleue'   => "L'Orange Bleue",
    'cercle'         => 'Cercle',
    'episod'         => 'Episod',
    'magic_form'     => 'Magic Form',
    _                => brand,
  };

  factory Gym.fromJson(Map<String, dynamic> json) => Gym(
    id:           json['id'] as String,
    name:         json['name'] as String,
    brand:        json['brand'] as String,
    address:      json['address'] as String,
    city:         json['city'] as String,
    postalCode:   json['postal_code'] as String,
    country:      json['country'] as String,
    coachesCount: json['coaches_count'] as int? ?? 0,
    isFavorite:   json['is_favorite'] as bool? ?? false,
    latitude:     (json['latitude'] as num?)?.toDouble(),
    longitude:    (json['longitude'] as num?)?.toDouble(),
  );

  Map<String, dynamic> toJson() => {
    'id':           id,
    'name':         name,
    'brand':        brand,
    'address':      address,
    'city':         city,
    'postal_code':  postalCode,
    'country':      country,
    'coaches_count':coachesCount,
    'is_favorite':  isFavorite,
    if (latitude != null)  'latitude':  latitude,
    if (longitude != null) 'longitude': longitude,
  };

  Gym copyWith({bool? isFavorite}) => Gym(
    id:           id,
    name:         name,
    brand:        brand,
    address:      address,
    city:         city,
    postalCode:   postalCode,
    country:      country,
    coachesCount: coachesCount,
    isFavorite:   isFavorite ?? this.isFavorite,
    latitude:     latitude,
    longitude:    longitude,
  );

  @override
  List<Object?> get props => [id, name, brand, city, postalCode, country];
}

package com.mycoach.app

import android.app.Application
import android.content.Context
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.mycoach.app.api.ApiClient

val Context.dataStore by preferencesDataStore(name = "settings")

object Prefs {
    val SERVER_URL = stringPreferencesKey("server_url")
    const val DEFAULT_URL = "http://192.168.1.100:8000"
}

class MyCoachApp : Application() {
    override fun onCreate() {
        super.onCreate()
        // Will be initialized with saved URL in MainActivity
        ApiClient.init(Prefs.DEFAULT_URL)
    }
}

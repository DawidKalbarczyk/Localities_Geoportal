import { Component, inject, signal } from '@angular/core';
import { AuthorBar } from '../global-components/author-bar/author-bar';
import {LoginCorner} from '../global-components/login-corner/login-corner';
import { ReturnCorner } from '../global-components/return-corner/return-corner';
import { RouterLink } from '@angular/router';
import { DarkMode } from '../services/dark-mode/dark-mode';
import { LoginService } from '../services/login-service/login-service';
import { GeoserverService } from '../services/GeoserverService/geoserver-service';
import { TranslatePipe } from '../pipes/translate.pipe';

@Component({
  selector: 'app-home',
  imports: [AuthorBar, LoginCorner, ReturnCorner, RouterLink, TranslatePipe],
  templateUrl: './home.html',
  styleUrl: './home.scss',
})
export class Home {
  private loginService = inject(LoginService);

  public isDarkMode = inject(DarkMode).isDarkMode;
  public isLoggedIn = this.loginService.isLoggedIn;

  
  public wasMiddleClicked = signal<boolean>(false);
  public wasPopUpCloseClicked = signal<boolean>(false);

  middleClickHandler() {
    this.wasMiddleClicked.set(!this.wasMiddleClicked());
  }

  wasPopUpBgClicked() {
    this.wasPopUpCloseClicked.set(true);
    setTimeout(() => {
      this.wasMiddleClicked.set(false);
      this.wasPopUpCloseClicked.set(false);
    }, 500); 
  }
  public currentUserData: any;

  async loginWithGoogle() {
    try {
      this.currentUserData = await this.loginService.componentLoginGoogle()
      this.loginService.userData.set(this.currentUserData);
      console.log('Email: ', this.currentUserData.email);
      console.log('Display Name: ', this.currentUserData.displayName);
      console.log('Photo URL: ', this.currentUserData.photoURL);
      console.log('UID: ', this.currentUserData.uid);
    } catch (error) {
    console.error('Login failed:', error);
    window.alert('Logowanie przez Google nie powiodło się.');
    return;
    } 
  }

  public GeoserverService = inject(GeoserverService);

  createTempGeo() {
    const userStringCheck = this.loginService.userData()?.uid;
    let userId: string = '';
    if (userStringCheck) {
      userId = userStringCheck;
    }
    this.GeoserverService.createTempWorkspace(userId).subscribe({
      next: (response) => {
        console.log('Temp workspace created:', response);
      },
      error: (error) => {
        console.error('Error creating temp workspace:', error);
      }
    });
    this.GeoserverService.createTempDatastore(userId).subscribe({
      next: (response) => {
        console.log('Temp datastore created:', response);
      },
      error: (error) => {
        console.error('Error creating temp datastore:', error);
      }
    });
  }

}

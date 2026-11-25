import { Component, inject } from '@angular/core';
import { AuthorBar } from '../../global-components/author-bar/author-bar';
import { LoginCorner } from '../../global-components/login-corner/login-corner';
import { ReturnCorner } from '../../global-components/return-corner/return-corner';
import { NavigationEnd, Router, RouterOutlet } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { filter, map } from 'rxjs';
import { PopUpService } from '../../services/pop-up-service/pop-up-service';
import { PopUp } from '../../global-components/pop-up/pop-up';

@Component({
  selector: 'app-history',
  imports: [AuthorBar, LoginCorner, ReturnCorner, RouterOutlet, PopUp],
  templateUrl: './history.html',
  styleUrl: './history.scss',
})
export class History {
  private router = inject(Router);
  public PopUpService = inject(PopUpService);

public url = toSignal(
  this.router.events.pipe(
    filter((event): event is NavigationEnd =>
      event instanceof NavigationEnd
    ),
    map(event => event.urlAfterRedirects)
  ),
  { initialValue: this.router.url }
);
} 

import { Component, inject } from '@angular/core';
import { AuthorBar } from '../../global-components/author-bar/author-bar';
import { LoginCorner } from '../../global-components/login-corner/login-corner';
import { ReturnCorner } from '../../global-components/return-corner/return-corner';
import { PopUpService } from '../../services/pop-up-service/pop-up-service';
import { PopUp } from '../../global-components/pop-up/pop-up';


@Component({
  selector: 'app-search',
  imports: [AuthorBar, LoginCorner, ReturnCorner, PopUp],
  templateUrl: './search.html',
  styleUrl: './search.scss',
})
export class Search {
  public PopUpService = inject(PopUpService);
}
